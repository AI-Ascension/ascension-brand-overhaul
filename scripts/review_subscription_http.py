#!/usr/bin/env python3
"""Exercise a website checkout over loopback HTTP and a TLS SMTP sink.

Uses synthetic addresses, disposable storage, and an in-memory SMTP sink that
never forwards mail. Does not use deployment credentials or existing state.
"""
from __future__ import annotations

import argparse
import email
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import socketserver
import shutil
import ssl
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("website", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    website = args.website.resolve(strict=True)
    if args.output.exists():
        parser.error("output must be a new file")
    if shutil.which("php") is None or shutil.which("openssl") is None:
        parser.error("php and openssl must be available on PATH")
    checks = []
    messages = []
    completed = False
    def source_hashes():
        return {str(path.relative_to(website)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((website / "api").glob("*.php"))}
    initial_source = source_hashes()

    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)

    with tempfile.TemporaryDirectory(prefix="ascension-http-review-") as temporary:
        root = Path(temporary)
        cert, key = root / "cert.pem", root / "key.pem"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=127.0.0.2", "-addext", "subjectAltName=IP:127.0.0.2", "-keyout", str(key), "-out", str(cert)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain(cert, key)

        class Sink(socketserver.StreamRequestHandler):
            def handle(self):
                def reply(value):
                    self.wfile.write(value + b"\r\n")
                    self.wfile.flush()
                reply(b"220 localhost synthetic sink")
                recipients = []
                while line := self.rfile.readline(32768):
                    command = line.decode("ascii", "replace").strip()
                    verb = command.split(" ", 1)[0].upper()
                    if verb in {"EHLO", "HELO"}:
                        reply(b"250-localhost\r\n250 AUTH LOGIN")
                    elif verb == "AUTH":
                        reply(b"334 VXNlcm5hbWU6")
                        self.rfile.readline(1024)
                        reply(b"334 UGFzc3dvcmQ6")
                        self.rfile.readline(1024)
                        reply(b"235 authenticated synthetic credentials")
                    elif verb == "RCPT":
                        recipients.append(command)
                        reply(b"250 recipient accepted locally")
                    elif verb == "DATA":
                        reply(b"354 end with dot")
                        lines = []
                        while chunk := self.rfile.readline(32768):
                            if chunk == b".\r\n":
                                break
                            lines.append(chunk[1:] if chunk.startswith(b"..") else chunk)
                        messages.append((email.message_from_bytes(b"".join(lines)), list(recipients)))
                        reply(b"250 retained in memory only")
                    elif verb == "QUIT":
                        reply(b"221 closed")
                        return
                    else:
                        reply(b"250 ok")

        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True
            def get_request(self):
                connection, address = super().get_request()
                connection.settimeout(10)
                return tls.wrap_socket(connection, server_side=True), address

        smtp = Server(("127.0.0.2", 0), Sink)
        smtp_thread = threading.Thread(target=smtp.serve_forever, daemon=True)
        smtp_thread.start()
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        store = root / "store"
        store.mkdir()
        environment = {key: value for key, value in os.environ.items() if not key.startswith(("MAILINGLIST_", "AIASCENSION_"))}
        environment.update(AIASCENSION_STORE_ROOT=str(store), MAILINGLIST_SMTP_HOST="127.0.0.2", MAILINGLIST_SMTP_PORT=str(smtp.server_address[1]), MAILINGLIST_SMTP_USER="synthetic", MAILINGLIST_SMTP_PASS="synthetic", MAILINGLIST_FROM="sender@example.invalid", MAILINGLIST_NOTIFY_TO="operator@example.invalid", MAILINGLIST_CONFIRM_URL=base + "/api/confirm.php", MAILINGLIST_UNSUBSCRIBE_URL=base + "/api/unsubscribe.php")
        log = (root / "php.log").open("wb")
        php = subprocess.Popen(["php", "-d", f"openssl.cafile={cert}", "-S", f"127.0.0.1:{port}", "-t", str(website)], env=environment, stdout=log, stderr=log)
        smtp_running = True

        def request(path, body=None, *, accept="application/json", extra=None, raw=None):
            headers = {"Accept": accept}
            if body is not None or raw is not None:
                headers["Content-Type"] = "application/json"
            headers.update(extra or {})
            payload = json.dumps(body).encode() if body is not None else raw
            try:
                response = urllib.request.urlopen(urllib.request.Request(base + path, data=payload, headers=headers), timeout=15)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                return response.status, response.headers, response.read().decode()

        def state():
            return json.loads((store / "app_data/subscriptions.json").read_text())

        def reset_limit():
            # This belongs exclusively to this disposable test store.
            (store / "app_data/rate_limits.json").write_text("{}")

        try:
            for _ in range(100):
                if php.poll() is not None:
                    raise RuntimeError("local PHP server exited")
                try:
                    request("/")
                    break
                except urllib.error.URLError:
                    time.sleep(.05)
            check("GET subscription rejects method", request("/api/subscribe.php")[0] == 405)
            payload = {"email": "visitor@example.invalid", "consent": True, "source": "website\r\nBcc: injected@example.invalid<script>x</script>"}
            check("foreign origin denied", request("/api/subscribe.php", payload, extra={"Origin": "https://untrusted.invalid"})[0] == 403)
            check("malformed JSON rejected", request("/api/subscribe.php", raw=b"{")[0] == 400)
            check("oversized request rejected", request("/api/subscribe.php", raw=b"x" * 16385)[0] == 413)
            check("missing consent rejected", request("/api/subscribe.php", {**payload, "consent": False})[0] == 422)
            check("invalid address rejected", request("/api/subscribe.php", {**payload, "email": "invalid"})[0] == 422)
            request("/api/subscribe.php", {**payload, "_hp": "bot"})
            check("honeypot has no storage or mail", not (store / "app_data/subscriptions.json").exists() and not messages)
            status, headers, response = request("/api/subscribe.php", payload)
            check("subscription gives generic no-store response", status == 200 and headers["Cache-Control"] == "no-store" and headers["Referrer-Policy"] == "no-referrer" and "visitor@" not in response)
            check("TLS mail and operator notice received locally", len(messages) == 2)
            confirmation = next(message for message, _ in messages if str(message["Subject"]).startswith("Confirm your"))
            text = confirmation.get_payload(decode=True).decode()
            confirm_path = re.search(r"/api/confirm\.php\?token=[a-f0-9]+", text).group()
            unsubscribe_path = re.search(r"/api/unsubscribe\.php\?token=[a-f0-9]+", text).group()
            check("mail has no injected headers or recipients", all(message.get("Bcc") is None and message.get_content_type() == "text/plain" and len(recipients) == 1 for message, recipients in messages))
            pending = next(iter(state()["pending"].values()))
            check("successful delivery remains pending until confirmation", not state()["active"] and pending["deliveryStatus"] == "sent")
            duplicate = request("/api/subscribe.php", payload)
            check("duplicate suppresses mail and matches generic response", duplicate[2] == response and len(messages) == 2)
            status, headers, html = request(confirm_path, accept="text/html")
            check("confirmation returns readable HTML without token", status == 200 and "Subscription confirmed" in html and confirm_path.split("=")[1] not in html and headers["Referrer-Policy"] == "no-referrer")
            check("confirmed state active", len(state()["active"]) == 1 and not state()["pending"])
            check("confirmation replay rejected", request(confirm_path)[0] == 400)
            check("active duplicate suppresses mail", request("/api/subscribe.php", payload)[2] == response and len(messages) == 2)
            check("unsubscribe HTML removes active state", request(unsubscribe_path, accept="text/html")[0] == 200 and not state()["active"])
            check("unsubscribe replay remains generic", request(unsubscribe_path)[0] == 200)
            check("invalid HTML link has readable error", request("/api/confirm.php?token=invalid", accept="text/html")[0] == 400)
            reset_limit()
            smtp.shutdown()
            smtp.server_close()
            smtp_running = False
            failed_payload = {**payload, "email": "failure@example.invalid"}
            check("mail failure gives non-enumerating response", request("/api/subscribe.php", failed_payload)[2] == response)
            failed_state = state()
            failed_record = next(iter(failed_state["pending"].values()))
            check("failed delivery is recorded without activation", failed_record["deliveryStatus"] == "failed" and not failed_state["active"])
            check("immediate failed-delivery retry is bounded", request("/api/subscribe.php", failed_payload)[0] == 200 and next(iter(state()["pending"].values()))["deliveryAttempts"] == 1)
            for _ in range(3):
                request("/api/subscribe.php", failed_payload)
            check("sixth valid request is rate limited", request("/api/subscribe.php", failed_payload)[0] == 429)
            reset_limit()
            # Advance only the synthetic record's retry clock; the HTTP
            # endpoint itself retains its real cooldown and expiry policy.
            failed_record["deliveryLastAttemptAt"] = int(time.time()) - 301
            (store / "app_data/subscriptions.json").write_text(json.dumps(failed_state))
            smtp = Server(smtp.server_address, Sink)
            smtp_thread = threading.Thread(target=smtp.serve_forever, daemon=True)
            smtp_thread.start()
            smtp_running = True
            request("/api/subscribe.php", failed_payload)
            recovered_state = state()
            check("retry after cooldown delivers a rotated token", len(messages) == 3 and next(iter(recovered_state["pending"].values()))["deliveryStatus"] == "sent" and set(recovered_state["pending"]) != set(failed_state["pending"]))
            recovered_text = messages[-1][0].get_payload(decode=True).decode()
            recovered_path = re.search(r"/api/confirm\.php\?token=[a-f0-9]+", recovered_text).group()
            check("raw confirmation token absent from persisted state", recovered_path.split("=")[1] not in json.dumps(recovered_state))
            next(iter(recovered_state["pending"].values()))["expiresAt"] = int(time.time()) - 1
            (store / "app_data/subscriptions.json").write_text(json.dumps(recovered_state))
            check("expired confirmation cannot activate", request(recovered_path, accept="text/html")[0] == 400 and not state()["active"])
            # A file in place of the disposable data directory creates a real
            # storage failure, without relying on permissions while running root.
            data = store / "app_data"
            data.rename(store / "saved-test-data")
            data.write_text("synthetic storage fault")
            check("storage failure returns sanitized 503", request("/api/subscribe.php", payload)[0] == 503)
            check("confirmation storage failure returns 503", request(confirm_path, accept="text/html")[0] == 503)
            check("unsubscribe storage failure returns 503", request(unsubscribe_path, accept="text/html")[0] == 503)
            check("API source unchanged throughout HTTP review", initial_source == source_hashes())
            completed = True
        finally:
            php.terminate()
            try:
                php.wait(timeout=5)
            except subprocess.TimeoutExpired:
                php.kill()
                php.wait()
            log.close()
            if smtp_running:
                smtp.shutdown()
                smtp.server_close()
            smtp_thread.join(timeout=2)
            source = source_hashes()
            report = {"schema_version": "ai-ascension.subscription-http-review.v1", "scope": "Synthetic loopback HTTP and TLS SMTP sink; no live host, real inbox delivery, or deployment proof", "checks": checks, "pass": completed and all(item["pass"] for item in checks), "source_files_sha256": source}
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x") as output:
                json.dump(report, output, indent=2)
                output.write("\n")
            print(json.dumps({"checks": len(checks), "pass": report["pass"]}))


if __name__ == "__main__":
    main()
