import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.function.Consumer;
import java.awt.Desktop;

public class SmartInterface extends Application {
    private TabPane tabPane;
    private Tab mathTab, dateTab, addressTab, aboutTab;
    private TextArea latexTextArea;
    private Button screenshotButton;
    private ClipboardMonitor clipboardMonitor;
    private HttpClient httpClient;
    private static ClipboardMonitor monitorRef = null;
    private String currentAddressText = "";
    private TextArea addressTextArea;
    private Button getDirectionsButton;
    private String currentDateText = "";
    private TextArea dateTextArea;
    private TextArea eventDescriptionArea;
    private Button createCalendarEventButton;
    private Button clearCalendarButton;
    private Label calendarSuccessLabel;
    private Button downloadButton;

    
    public SmartInterface() {
        this.clipboardMonitor = new ClipboardMonitor();
        this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("ClipSmart");
        
        tabPane = new TabPane();
        
        createMathTab();
        createAddressTab();
        createAboutTab();
        
        tabPane.getTabs().addAll(mathTab, addressTab, aboutTab);
        
        Scene scene = new Scene(tabPane, 600, 400);
        scene.getStylesheets().add(getClass().getResource("/resources/styles.css").toExternalForm());
        primaryStage.setScene(scene);
        primaryStage.setOnCloseRequest(e -> {
            primaryStage.hide();
            e.consume();
        });
        primaryStage.show();
    }
    
    private void createMathTab() {
        mathTab = new Tab("Math");
        mathTab.setClosable(false);
        
        VBox mathContent = new VBox(10);
        mathContent.setPadding(new Insets(15));
        mathContent.setAlignment(Pos.TOP_CENTER);
        
        Label titleLabel = new Label("Math Content Processor");
        titleLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        screenshotButton = new Button("Take Screenshot for LaTeX");
        screenshotButton.setStyle("-fx-min-width: 200px; -fx-min-height: 40px;");
        screenshotButton.setOnAction(e -> takeScreenshot());
        
        Label latexLabel = new Label("LaTeX Transcription:");
        latexLabel.setStyle("-fx-font-weight: bold;");
        
        latexTextArea = new TextArea();
        latexTextArea.setPromptText("LaTeX transcription will appear here...");
        latexTextArea.setPrefRowCount(15);
        latexTextArea.setWrapText(true);
        latexTextArea.setEditable(false);
        
        // Add context menu for copying
        ContextMenu contextMenu = new ContextMenu();
        MenuItem copyItem = new MenuItem("Copy");
        copyItem.setOnAction(e -> {
            ClipboardMonitor.setIgnoreNextClipboardChange();
            latexTextArea.copy();
        });
        contextMenu.getItems().add(copyItem);
        latexTextArea.setContextMenu(contextMenu);
        
        latexTextArea.setOnKeyPressed(e -> {
            if (e.isControlDown() && e.getCode().toString().equals("C")) {
                ClipboardMonitor.setIgnoreNextClipboardChange();
                latexTextArea.copy();
            }
        });
        
        mathContent.getChildren().addAll(titleLabel, screenshotButton, latexLabel, latexTextArea);
        mathTab.setContent(mathContent);
    }
    
    private void createDateTab() {
        dateTab = new Tab("Date/Time");
        dateTab.setClosable(false);
        
        HBox mainContent = new HBox(15);
        mainContent.setPadding(new Insets(15));
        
        VBox leftContent = new VBox(10);
        leftContent.setAlignment(Pos.TOP_CENTER);
        leftContent.setPrefWidth(400);
        
        Label titleLabel = new Label("Calendar Event Creator");
        titleLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        Label dateLabel = new Label("Detected Date/Time:");
        dateLabel.setStyle("-fx-font-weight: bold;");
        
        dateTextArea = new TextArea();
        dateTextArea.setPromptText("No date/time detected in clipboard...");
        dateTextArea.setPrefRowCount(3);
        dateTextArea.setWrapText(true);
        dateTextArea.setEditable(true);
        
        Label descriptionLabel = new Label("Event Description:");
        descriptionLabel.setStyle("-fx-font-weight: bold;");
        
        eventDescriptionArea = new TextArea();
        eventDescriptionArea.setPromptText("Enter a description for your calendar event...");
        eventDescriptionArea.setPrefRowCount(4);
        eventDescriptionArea.setWrapText(true);
        eventDescriptionArea.setEditable(true);
        
        createCalendarEventButton = new Button("Create Calendar Event (.ics)");
        createCalendarEventButton.setStyle("-fx-min-width: 250px; -fx-min-height: 40px;");
        createCalendarEventButton.setDisable(true);
        createCalendarEventButton.setOnAction(e -> createCalendarEvent());
        
        Label instructionLabel = new Label("Edit the date/time above and add an event description, then click 'Create Calendar Event'");
        instructionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666666;");
        instructionLabel.setWrapText(true);
        
        leftContent.getChildren().addAll(titleLabel, dateLabel, dateTextArea, 
                                        descriptionLabel, eventDescriptionArea,
                                        createCalendarEventButton, instructionLabel);
        
        VBox rightContent = new VBox(10);
        rightContent.setAlignment(Pos.TOP_CENTER);
        rightContent.setPrefWidth(150);
        
        calendarSuccessLabel = new Label("");
        calendarSuccessLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #00AA00; -fx-font-weight: bold;");
        calendarSuccessLabel.setWrapText(true);
        calendarSuccessLabel.setVisible(false);
        
        downloadButton = new Button("Download .ics");
        downloadButton.getStyleClass().add("download-button");
        downloadButton.setStyle("-fx-min-width: 100px; -fx-min-height: 30px;");
        downloadButton.setVisible(false);
        
        clearCalendarButton = new Button("Clear");
        clearCalendarButton.setStyle("-fx-min-width: 100px; -fx-min-height: 30px;");
        clearCalendarButton.setOnAction(e -> clearCalendarFields());
        
        rightContent.getChildren().addAll(calendarSuccessLabel, downloadButton, clearCalendarButton);
        
        mainContent.getChildren().addAll(leftContent, rightContent);
        
        ContextMenu contextMenu = new ContextMenu();
        MenuItem copyItem = new MenuItem("Copy Date/Time");
        copyItem.setOnAction(e -> {
            ClipboardMonitor.setIgnoreNextClipboardChange();
            dateTextArea.copy();
        });
        contextMenu.getItems().add(copyItem);
        dateTextArea.setContextMenu(contextMenu);
        
        dateTextArea.textProperty().addListener((observable, oldValue, newValue) -> {
            updateCreateEventButtonState();
        });
        
        eventDescriptionArea.textProperty().addListener((observable, oldValue, newValue) -> {
            updateCreateEventButtonState();
        });
        
        dateTab.setContent(mainContent);
    }
    
    private void createAddressTab() {
        addressTab = new Tab("Addresses");
        addressTab.setClosable(false);
        
        VBox addressContent = new VBox(10);
        addressContent.setPadding(new Insets(15));
        addressContent.setAlignment(Pos.TOP_CENTER);
        
        Label titleLabel = new Label("Address Manager");
        titleLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        Label addressLabel = new Label("Detected Address:");
        addressLabel.setStyle("-fx-font-weight: bold;");
        
        addressTextArea = new TextArea();
        addressTextArea.setPromptText("No address detected in clipboard...");
        addressTextArea.setPrefRowCount(4);
        addressTextArea.setWrapText(true);
        addressTextArea.setEditable(true);
        
        getDirectionsButton = new Button("Get Directions in Google Maps");
        getDirectionsButton.setStyle("-fx-min-width: 250px; -fx-min-height: 40px;");
        getDirectionsButton.setDisable(true);
        getDirectionsButton.setOnAction(e -> openGoogleMapsDirections());
        
        Label instructionLabel = new Label("Edit the address above if needed, then click 'Get Directions'");
        instructionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666666;");
        instructionLabel.setWrapText(true);
        
        ContextMenu contextMenu = new ContextMenu();
        MenuItem copyItem = new MenuItem("Copy Address");
        copyItem.setOnAction(e -> {
            ClipboardMonitor.setIgnoreNextClipboardChange();
            addressTextArea.copy();
        });
        contextMenu.getItems().add(copyItem);
        addressTextArea.setContextMenu(contextMenu);
        
        addressTextArea.textProperty().addListener((observable, oldValue, newValue) -> {
            getDirectionsButton.setDisable(newValue == null || newValue.trim().isEmpty());
        });
        
        addressContent.getChildren().addAll(titleLabel, addressLabel, addressTextArea, 
                                          getDirectionsButton, instructionLabel);
        addressTab.setContent(addressContent);
    }
    
    private void createAboutTab() {
        aboutTab = new Tab("About");
        aboutTab.setClosable(false);
        
        VBox aboutContent = new VBox(15);
        aboutContent.setPadding(new Insets(20));
        aboutContent.setAlignment(Pos.TOP_CENTER);
        
        Label titleLabel = new Label("ClipSmart");
        titleLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #2196F3;");
        
        Label versionLabel = new Label("Version 1.0");
        versionLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #666666;");
        
        Label descriptionLabel = new Label("A clipboard that thinks before pasting.");
        descriptionLabel.setStyle("-fx-font-size: 16px; -fx-text-fill: #333333;");
        
        VBox featuresBox = new VBox(8);
        featuresBox.setAlignment(Pos.TOP_LEFT);
        featuresBox.setMaxWidth(400);
        
        Label featuresTitle = new Label("Features:");
        featuresTitle.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        
        Label mathFeature = new Label("• Math Content: Take screenshots and convert to LaTeX");
        mathFeature.setStyle("-fx-font-size: 12px;");
        mathFeature.setWrapText(true);
        
        Label addressFeature = new Label("• Address Detection: Automatically detect addresses and get directions");
        addressFeature.setStyle("-fx-font-size: 12px;");
        addressFeature.setWrapText(true);
        
        featuresBox.getChildren().addAll(featuresTitle, mathFeature, addressFeature);
        
        Label copyrightLabel = new Label("© 2025 ClipSmart. All rights reserved.");
        copyrightLabel.setStyle("-fx-font-size: 10px; -fx-text-fill: #999999;");
        
        aboutContent.getChildren().addAll(titleLabel, versionLabel, descriptionLabel, featuresBox, copyrightLabel);
        aboutTab.setContent(aboutContent);
    }
    
    private void takeScreenshot() {
        Platform.runLater(() -> {
            Stage stage = (Stage) screenshotButton.getScene().getWindow();
            stage.setIconified(true);
        });
        
        new Thread(() -> {
            try {
                Thread.sleep(500);
                clipboardMonitor.captureScreenArea(this::processScreenshotForLatex);
            } catch (InterruptedException e) {
                System.err.println("Screenshot capture interrupted: " + e.getMessage());
            }
        }).start();
    }
    
    private String extractLatexFromResponse(String jsonResponse) {
        try {
            String searchKey = "\"latex_conversion\":\"";
            int startIndex = jsonResponse.indexOf(searchKey);
            if (startIndex == -1) {
                return "No LaTeX content found in response.";
            }
            
            startIndex += searchKey.length();
            int endIndex = jsonResponse.indexOf("\"", startIndex);
            if (endIndex == -1) {
                return "Malformed response - could not extract LaTeX content.";
            }
            
            String latexContent = jsonResponse.substring(startIndex, endIndex);
            
            // Clean up escape characters and formatting
            latexContent = latexContent
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\\"", "\"");
            
            latexContent = latexContent
                .replaceAll("^```latex\\s*", "")
                .replaceAll("\\s*```$", "")
                .trim();
            
            return latexContent;
            
        } catch (Exception e) {
            return "Error parsing response: " + e.getMessage();
        }
    }
    
    private void processScreenshotForLatex(BufferedImage image) {
        Platform.runLater(() -> {
            Stage stage = (Stage) screenshotButton.getScene().getWindow();
            stage.setIconified(false);
            stage.toFront();
        });
        
        if (image == null) {
            Platform.runLater(() -> {
                latexTextArea.setText("Screenshot capture was cancelled or failed.");
            });
            return;
        }
        
        Platform.runLater(() -> {
            latexTextArea.setText("Processing screenshot for LaTeX conversion...");
        });
        
        new Thread(() -> {
            try {
                String base64Image = clipboardMonitor.encodeImageToBase64(image);
                if (base64Image == null) {
                    Platform.runLater(() -> {
                        latexTextArea.setText("Error: Failed to encode screenshot.");
                    });
                    return;
                }
                
                String jsonBody = "{\"image\":\"" + base64Image + "\",\"type\":\"screenshot\"}";
                
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:8000/process-image"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                    .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                Platform.runLater(() -> {
                    String responseBody = response.body();
                    if (response.statusCode() == 200) {
                        String latexContent = extractLatexFromResponse(responseBody);
                        latexTextArea.setText(latexContent);
                    } else {
                        latexTextArea.setText("Error processing screenshot: " + responseBody);
                    }
                });
                
            } catch (IOException | InterruptedException e) {
                Platform.runLater(() -> {
                    latexTextArea.setText("Error sending screenshot to API: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private void openGoogleMapsDirections() {
        String address = addressTextArea.getText().trim();
        if (address.isEmpty()) {
            showAlert("Error", "Please enter an address first.");
            return;
        }
        
        try {
            String encodedAddress = URLEncoder.encode(address, StandardCharsets.UTF_8);
            String googleMapsUrl = "https://www.google.com/maps/dir/?api=1&destination=" + encodedAddress;
            
            System.out.println("Opening Google Maps with URL: " + googleMapsUrl);
            
            if (Desktop.isDesktopSupported()) {
                Desktop desktop = Desktop.getDesktop();
                if (desktop.isSupported(Desktop.Action.BROWSE)) {
                    desktop.browse(new URI(googleMapsUrl));
                } else {
                    showAlert("Error", "Browser not supported on this system.");
                }
            } else {
                showAlert("Error", "Desktop not supported on this system.");
            }
        } catch (Exception e) {
            System.err.println("Error opening Google Maps: " + e.getMessage());
            showAlert("Error", "Failed to open Google Maps: " + e.getMessage());
        }
    }
    
    private void updateCreateEventButtonState() {
        if (createCalendarEventButton != null && dateTextArea != null && eventDescriptionArea != null) {
            String dateText = dateTextArea.getText();
            String description = eventDescriptionArea.getText();
            createCalendarEventButton.setDisable(
                dateText == null || dateText.trim().isEmpty() || 
                description == null || description.trim().isEmpty()
            );
        }
    }
    
    private void clearCalendarFields() {
        if (dateTextArea != null) {
            dateTextArea.clear();
        }
        if (eventDescriptionArea != null) {
            eventDescriptionArea.clear();
        }
        if (calendarSuccessLabel != null) {
            calendarSuccessLabel.setVisible(false);
            calendarSuccessLabel.getStyleClass().clear();
            calendarSuccessLabel.getStyleClass().add("success-label");
            calendarSuccessLabel.setStyle("-fx-font-size: 12px;");
        }
        if (downloadButton != null) {
            downloadButton.setVisible(false);
        }
    }
    
    private void createCalendarEvent() {
        String dateText = dateTextArea.getText().trim();
        String description = eventDescriptionArea.getText().trim();
        
        if (dateText.isEmpty()) {
            showAlert("Error", "Please enter a date/time first.");
            return;
        }
        
        if (description.isEmpty()) {
            showAlert("Error", "Please enter an event description.");
            return;
        }
        
        new Thread(() -> {
            try {
                String jsonBody = String.format(
                    "{\"text\":\"%s\",\"description\":\"%s\"}", 
                    dateText.replace("\"", "\\\""), 
                    description.replace("\"", "\\\"")
                );
                
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:8000/create-calendar-event"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                    .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                Platform.runLater(() -> {
                    if (response.statusCode() == 200) {
                        String responseBody = response.body();
                        System.out.println("Calendar event response: " + responseBody);
                        
                        calendarSuccessLabel.setText("Calendar event created successfully!");
                        calendarSuccessLabel.getStyleClass().clear();
                        calendarSuccessLabel.getStyleClass().add("success-label");
                        calendarSuccessLabel.setStyle("-fx-font-size: 12px;");
                        calendarSuccessLabel.setVisible(true);
                        
                        // Extract download URL if available and show download button
                        if (responseBody.contains("\"download_url\"")) {
                            String downloadUrl = extractValueFromJson(responseBody, "download_url");
                            if (downloadUrl != null && !downloadUrl.isEmpty()) {
                                downloadButton.setOnAction(e -> openUrlInBrowser(downloadUrl));
                                downloadButton.setVisible(true);
                                calendarSuccessLabel.setText("Calendar event created!\nClick Download to get .ics file");
                            }
                        }
                    } else {
                        String responseBody = response.body();
                        String errorMessage = extractValueFromJson(responseBody, "error");
                        calendarSuccessLabel.setText("Error: Failed to create event");
                        calendarSuccessLabel.getStyleClass().clear();
                        calendarSuccessLabel.getStyleClass().add("error-label");
                        calendarSuccessLabel.setStyle("-fx-font-size: 12px;");
                        calendarSuccessLabel.setVisible(true);
                        downloadButton.setVisible(false);
                        showAlert("Error", "Failed to create calendar event: " + 
                                 (errorMessage != null ? errorMessage : responseBody));
                    }
                });
                
            } catch (IOException | InterruptedException e) {
                Platform.runLater(() -> {
                    showAlert("Error", "Failed to connect to calendar service: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private String extractValueFromJson(String json, String key) {
        try {
            String searchKey = "\"" + key + "\":\"";
            int startIndex = json.indexOf(searchKey);
            if (startIndex == -1) {
                return null;
            }
            
            startIndex += searchKey.length();
            int endIndex = json.indexOf("\"", startIndex);
            if (endIndex == -1) {
                return null;
            }
            
            return json.substring(startIndex, endIndex);
        } catch (Exception e) {
            return null;
        }
    }
    
    private void showCalendarEventSuccess(String downloadUrl) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Calendar Event Created");
        alert.setHeaderText("Your calendar event has been created successfully!");
        alert.setContentText("Click OK to download the .ics file, or copy the link below:\n\n" + downloadUrl);
        
        ButtonType downloadButton = new ButtonType("Download", ButtonBar.ButtonData.OK_DONE);
        ButtonType copyLinkButton = new ButtonType("Copy Link", ButtonBar.ButtonData.OTHER);
        ButtonType cancelButton = new ButtonType("Close", ButtonBar.ButtonData.CANCEL_CLOSE);
        
        alert.getButtonTypes().setAll(downloadButton, copyLinkButton, cancelButton);
        
        alert.showAndWait().ifPresent(buttonType -> {
            if (buttonType == downloadButton) {
                openUrlInBrowser(downloadUrl);
            } else if (buttonType == copyLinkButton) {
                ClipboardMonitor.setIgnoreNextClipboardChange();
                copyToClipboard(downloadUrl);
                showAlert("Copied", "Download link copied to clipboard!");
            }
        });
    }
    
    private void copyToClipboard(String text) {
        javafx.scene.input.Clipboard clipboard = javafx.scene.input.Clipboard.getSystemClipboard();
        javafx.scene.input.ClipboardContent content = new javafx.scene.input.ClipboardContent();
        content.putString(text);
        clipboard.setContent(content);
    }
    
    private void openUrlInBrowser(String url) {
        try {
            if (Desktop.isDesktopSupported()) {
                Desktop desktop = Desktop.getDesktop();
                if (desktop.isSupported(Desktop.Action.BROWSE)) {
                    desktop.browse(new URI(url));
                } else {
                    showAlert("Error", "Browser not supported on this system.");
                }
            } else {
                showAlert("Error", "Desktop not supported on this system.");
            }
        } catch (Exception e) {
            System.err.println("Error opening URL: " + e.getMessage());
            showAlert("Error", "Failed to open URL: " + e.getMessage());
        }
    }
    
    private void showAlert(String title, String message) {
        Platform.runLater(() -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle(title);
            alert.setHeaderText(null);
            alert.setContentText(message);
            alert.showAndWait();
        });
    }
    
    public void setAddressText(String addressText) {
        this.currentAddressText = addressText;
        if (addressTextArea != null) {
            Platform.runLater(() -> {
                addressTextArea.setText(addressText);
            });
        }
    }
    
    public void setDateText(String dateText) {
        this.currentDateText = dateText;
        if (dateTextArea != null) {
            Platform.runLater(() -> {
                dateTextArea.setText(dateText);
            });
        }
    }
    
    public void selectTabBasedOnContent(boolean isLink, boolean isDate, boolean isMath, boolean isAddress) {
        Platform.runLater(() -> {
            if (isMath && !isLink) {
                tabPane.getSelectionModel().select(mathTab);
            } else if (isAddress) {
                tabPane.getSelectionModel().select(addressTab);
            } else {
                tabPane.getSelectionModel().select(aboutTab);
            }
        });
    }
    
    public static void main(String[] args) {
        launch(args);
    }
    
    public static void launchNewInterface(boolean isLink, boolean isDate, boolean isMath, boolean isAddress, String originalText) {
        // Ensure JavaFX platform is running
        if (!Platform.isFxApplicationThread()) {
            Platform.setImplicitExit(false);
            Platform.runLater(() -> createNewWindow(isLink, isDate, isMath, isAddress, originalText));
        } else {
            createNewWindow(isLink, isDate, isMath, isAddress, originalText);
        }
    }
    
    public static void launchNewInterface(boolean isLink, boolean isDate, boolean isMath, boolean isAddress) {
        launchNewInterface(isLink, isDate, isMath, isAddress, "");
    }
    
    private static void createNewWindow(boolean isLink, boolean isDate, boolean isMath, boolean isAddress, String originalText) {
        try {
            SmartInterface app = new SmartInterface();
            monitorRef = app.clipboardMonitor;
            Stage stage = new Stage();
            stage.setTitle("Smart Interface - " + System.currentTimeMillis());
            stage.setAlwaysOnTop(true);
            app.start(stage);
            
            if (isAddress && originalText != null && !originalText.trim().isEmpty()) {
                app.setAddressText(originalText.trim());
            }
            
            
            app.selectTabBasedOnContent(isLink, isDate, isMath, isAddress);
        } catch (Exception e) {
            System.err.println("Error creating new interface window: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void createNewWindow(boolean isLink, boolean isDate, boolean isMath, boolean isAddress) {
        createNewWindow(isLink, isDate, isMath, isAddress, "");
    }

}