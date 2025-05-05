package Main;

import java.awt.Color;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.StringTokenizer;
import Data.Vector2D;
import Data.spriteInfo;
import logic.Control;
import timer.stopWatchX;
import FileIO.EZFileRead;

public class Main {
    // Fields (Static) below...
    public static Color c = new Color(200, 200, 75);
    public static boolean isImageDrawn = false;
    public static stopWatchX timer = new stopWatchX(250);

    // ArrayList to hold spriteInfo objects
    public static ArrayList<spriteInfo> sprites = new ArrayList<>();
    public static int currentSpriteIndex = 0;
    
    // HashMap to hold dialogue loaded from darkrai.txt
    public static HashMap<String, String> dialogueMap = new HashMap<>();

    public static void main(String[] args) {
        Control ctrl = new Control(); // Do NOT remove!
        ctrl.gameLoop(); // Do NOT remove!
    }

    /* This is your access to things BEFORE the game loop starts */
    public static void start() {
        // Load dialogue text from darkrai.txt
        EZFileRead ezrDialog = new EZFileRead("darkrai.txt");
        for (int i = 0; i < ezrDialog.getNumLines(); i++) {
            String raw = ezrDialog.getLine(i);
            // Use StringTokenizer to break the line into key and value using "*" as the delimiter
            StringTokenizer st = new StringTokenizer(raw, "*");
            String key = st.nextToken();
            String value = st.nextToken();
            dialogueMap.put(key, value);
        }
        
        int y = 500; // Fixed y-coordinate
        int step = 50; // Distance between each sprite on the x-axis
        int maxX = 1152; // 1280 - 128 (sprite width)

        for (int x = 0; x <= maxX; x += step) {
            String tag = "r" + ((x / step % 4) + 1); // Cycle through r1-r4
            sprites.add(new spriteInfo(new Vector2D(x, y), tag));
            System.out.println("Added sprite: " + tag + " at (" + x + ", " + y + ")");
        }
    }

    /* This is your access to the "game loop" */
    public static void update(Control ctrl) {
        if (timer.isTimeUp()) {
            currentSpriteIndex = (currentSpriteIndex + 1) % sprites.size();
            timer.resetWatch();
        }

        spriteInfo current = sprites.get(currentSpriteIndex);
        System.out.println("Displaying sprite: " + current.getTag() + " at (" + current.getCoords().getX() + ", " + current.getCoords().getY() + ")");
        ctrl.addSpriteToFrontBuffer(
            current.getCoords().getX(),
            current.getCoords().getY(),
            current.getTag()
        );
        
        // Retrieve one dialogue line from dialogueMap and display it at (100, 250)
        String dialogueLine = dialogueMap.get("string1");
        ctrl.drawString(100, 250, dialogueLine, Color.WHITE);
        
        ctrl.drawString(1000, 640, "Christian Zeidan", c);
    }
}
