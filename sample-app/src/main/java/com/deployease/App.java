
package com.deployease;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class App {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(
            new InetSocketAddress("127.0.0.1", 8081), 0
        );

        server.createContext("/", exchange -> {
            String html = """
                <html>
                <body style="font-family:Arial;text-align:center;
                             padding:80px;background:#eef5ff">
                  <h1>DeployEase Deployment Successful!</h1>
                  <h2>Java + Maven + Jenkins + Ansible</h2>
                  <p>Application deployed automatically.</p>
                </body>
                </html>
                """;

            byte[] data = html.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set(
                "Content-Type", "text/html; charset=UTF-8"
            );
            exchange.sendResponseHeaders(200, data.length);
            try (var out = exchange.getResponseBody()) {
                out.write(data);
            }
        });

        server.start();
        System.out.println("Application running on port 8081");
    }
}
// Automatic deployment test
// Automatic deployment test
