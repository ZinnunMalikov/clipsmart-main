import java.awt.*;
import java.awt.datatransfer.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.ByteArrayOutputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Base64;
import java.util.Scanner;
import java.util.function.Consumer;
import javax.imageio.ImageIO;
import javax.swing.*;
import javafx.application.Platform;
import javafx.embed.swing.JFXPanel;

public class ClipboardMonitor implements ClipboardOwner {
    private Clipboard clipboard;
    private String lastClipboardText = "";
    private HttpClient httpClient;
    public Robot robot;
    private static boolean ignoreNextClipboardChange = false;

    public ClipboardMonitor() {
        clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
        try {
            robot = new Robot();
        } catch (AWTException e) {
            System.err.println("Failed to create Robot: " + e.getMessage());
        }
        
        // Initialize JavaFX
        try {
            new JFXPanel();
            Platform.setImplicitExit(false);
            System.out.println("JavaFX initialized successfully");
        } catch (Exception e) {
            System.err.println("Failed to initialize JavaFX: " + e.getMessage());
        }
    }

    public void startMonitoring() {
        System.out.println("Starting clipboard monitor...");
        try {
            Transferable contents = clipboard.getContents(this);
            if (contents != null && contents.isDataFlavorSupported(DataFlavor.stringFlavor)) {
                lastClipboardText = (String) contents.getTransferData(DataFlavor.stringFlavor);
            }
            clipboard.setContents(contents, this);
        } catch (Exception e) {
            System.err.println("Error initializing clipboard: " + e.getMessage());
        }

        while (true) {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                break;
            }
        }
    }

    @Override
    public void lostOwnership(Clipboard clipboard, Transferable contents) {
        try {
            Thread.sleep(100);
            Transferable newContents = clipboard.getContents(this);
            if (newContents != null && newContents.isDataFlavorSupported(DataFlavor.stringFlavor)) {
                String newText = (String) newContents.getTransferData(DataFlavor.stringFlavor);
                if (!newText.equals(lastClipboardText)) {
                    lastClipboardText = newText;
                    
                    if (ignoreNextClipboardChange) {
                        System.out.println("Ignoring clipboard change from SmartInterface window");
                        ignoreNextClipboardChange = false;
                    } else {
                        System.out.println("Clipboard changed: " + newText.substring(0, Math.min(50, newText.length())) + "...");
                        sendToAPI(newText);
                    }
                }
            }
            clipboard.setContents(newContents, this);
        } catch (Exception e) {
            System.err.println("Error processing clipboard change: " + e.getMessage());
        }
    }

    private void sendToAPI(String text) {
        try {
            // Clean the text: remove newlines, convert backslashes to forward slashes, remove control chars
            String cleanedText = text
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("\t", " ")
                .replace("\\", "/")
                .replaceAll("\\p{Cntrl}", "")
                .replace("\"", "\\\"")
                .trim();
            
            String jsonBody = "{\"text\":\"" + cleanedText + "\"}";
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/process"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("API Response: " + response.body());

            parseAPIResponseAndLaunchInterface(response.body());
        } catch (IOException | InterruptedException e) {
            System.err.println("Error sending to API: " + e.getMessage());
        }
    }
    
    private void parseAPIResponseAndLaunchInterface(String responseBody) {
        try {
            System.out.println("DEBUG: Parsing API response: " + responseBody);
            
            boolean isLink = responseBody.contains("\"link\":true");
            boolean isDate = responseBody.contains("\"date\":true");
            boolean isMath = responseBody.contains("\"math\":true");
            boolean isAddress = responseBody.contains("\"address\":true");
            
            // Extract original text for address processing
            String originalText = "";
            String searchKey = "\"original_text\":\"";
            int startIndex = responseBody.indexOf(searchKey);
            if (startIndex != -1) {
                startIndex += searchKey.length();
                int endIndex = responseBody.indexOf("\"", startIndex);
                if (endIndex != -1) {
                    originalText = responseBody.substring(startIndex, endIndex);
                    originalText = originalText
                        .replace("\\\\", "\\")
                        .replace("\\n", "\n")
                        .replace("\\\"", "\"")
                        .replace("\\/", "/");
                }
            }
            
            System.out.println("Classification results:");
            System.out.println("Link: " + isLink + ", Date: " + isDate + ", Math: " + isMath + ", Address: " + isAddress);
            
            if (isLink || isDate || isMath || isAddress) {
                System.out.println("DEBUG: Attempting to launch interface...");
                final String textForInterface = originalText;
                try {
                    if (!Platform.isFxApplicationThread()) {
                        System.out.println("DEBUG: Not on FX thread, using Platform.runLater");
                        Platform.runLater(() -> {
                            System.out.println("DEBUG: Inside Platform.runLater");
                            SmartInterface.launchNewInterface(isLink, isDate, isMath, isAddress, textForInterface);
                        });
                    } else {
                        System.out.println("DEBUG: On FX thread, launching directly");
                        SmartInterface.launchNewInterface(isLink, isDate, isMath, isAddress, textForInterface);
                    }
                } catch (Exception launchException) {
                    System.err.println("Error launching interface: " + launchException.getMessage());
                    launchException.printStackTrace();
                }
            } else {
                System.out.println("DEBUG: No classification matched, not launching interface");
            }
            
        } catch (Exception e) {
            System.err.println("Error parsing API response: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void captureScreenArea(Consumer<BufferedImage> callback) {
        Rectangle screenRect = new Rectangle(Toolkit.getDefaultToolkit().getScreenSize());
        BufferedImage screenCapture = robot.createScreenCapture(screenRect);

        JFrame frame = new JFrame();
        frame.setUndecorated(true);
        frame.setExtendedState(JFrame.MAXIMIZED_BOTH);
        frame.setAlwaysOnTop(true);

        ScreenCapturePanel panel = new ScreenCapturePanel(screenCapture, selectedImage -> {
            frame.dispose();
            if (callback != null && selectedImage != null) callback.accept(selectedImage);
        });

        frame.add(panel);
        frame.setVisible(true);
    }

    private class ScreenCapturePanel extends JPanel {
        private Point startPoint, endPoint;
        private BufferedImage backgroundImage;
        private Consumer<BufferedImage> callback;

        public ScreenCapturePanel(BufferedImage screenshot, Consumer<BufferedImage> callback) {
            this.backgroundImage = screenshot;
            this.callback = callback;
            setCursor(Cursor.getPredefinedCursor(Cursor.CROSSHAIR_CURSOR));

            addMouseListener(new MouseAdapter() {
                @Override
                public void mousePressed(MouseEvent e) {
                    startPoint = e.getPoint();
                    endPoint = startPoint;
                    repaint();
                }

                @Override
                public void mouseReleased(MouseEvent e) {
                    endPoint = e.getPoint();
                    BufferedImage selected = captureSelectedArea();
                    if (callback != null) callback.accept(selected);
                }
            });

            addMouseMotionListener(new MouseMotionAdapter() {
                @Override
                public void mouseDragged(MouseEvent e) {
                    endPoint = e.getPoint();
                    repaint();
                }
            });
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            g.drawImage(backgroundImage, 0, 0, getWidth(), getHeight(), null);

            if (startPoint != null && endPoint != null) {
                Graphics2D g2d = (Graphics2D) g.create();

                int x = Math.min(startPoint.x, endPoint.x);
                int y = Math.min(startPoint.y, endPoint.y);
                int w = Math.abs(endPoint.x - startPoint.x);
                int h = Math.abs(endPoint.y - startPoint.y);

                g2d.setColor(new Color(0, 0, 0, 100)); // 100 = ~40% opacity
                g2d.fillRect(0, 0, getWidth(), getHeight());

                g2d.setClip(x, y, w, h);
                g2d.drawImage(backgroundImage, 0, 0, getWidth(), getHeight(), null);
                g2d.setClip(null);

                g2d.setColor(Color.RED);
                g2d.setStroke(new BasicStroke(2));
                g2d.drawRect(x, y, w, h);

                g2d.dispose();
            }
        }

        private BufferedImage captureSelectedArea() {
            if (startPoint == null || endPoint == null) return null;

            int x = Math.min(startPoint.x, endPoint.x);
            int y = Math.min(startPoint.y, endPoint.y);
            int w = Math.abs(endPoint.x - startPoint.x);
            int h = Math.abs(endPoint.y - startPoint.y);

            if (w == 0 || h == 0) return null;

            double scaleX = (double) backgroundImage.getWidth() / getWidth();
            double scaleY = (double) backgroundImage.getHeight() / getHeight();

            return backgroundImage.getSubimage(
                (int) (x * scaleX), (int) (y * scaleY),
                (int) (w * scaleX), (int) (h * scaleY)
            );
        }
    }

    public String encodeImageToBase64(BufferedImage image) {
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ImageIO.write(image, "png", baos);
            return Base64.getEncoder().encodeToString(baos.toByteArray());
        } catch (IOException e) {
            System.err.println("Error encoding image: " + e.getMessage());
            return null;
        }
    }

    private void sendScreenshotToAPI(BufferedImage image) {
        try {
            String base64Image = encodeImageToBase64(image);
            if (base64Image == null) return;

            String jsonBody = "{\"image\":\"" + base64Image + "\",\"type\":\"screenshot\"}";

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/process-image"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("Screenshot API Response: " + response.body());

        } catch (IOException | InterruptedException e) {
            System.err.println("Error sending screenshot to API: " + e.getMessage());
        }
    }

    public static void setIgnoreNextClipboardChange() {
        ignoreNextClipboardChange = true;
        System.out.println("Next clipboard change will be ignored");
    }

    public void onSmartInterfaceClosed() {
        System.out.println("Smart Interface closed. Ready to launch again.");
    }

    public static void main(String[] args) {
        ClipboardMonitor monitor = new ClipboardMonitor();
        if (args.length > 0 && args[0].equals("--capture")) {
            monitor.captureScreenArea(monitor::sendScreenshotToAPI);
        } else {
            monitor.startMonitoring();
        }
    }
}
