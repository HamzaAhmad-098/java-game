/* EZFileRead is a class created to simplify file input in Java. 
 * 
 * 2018 Matthew Phillips */

package FileIO;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;

public class EZFileRead {
    // Fields
    private BufferedReader in;
    private String file;
    private boolean isOpen;
    private ArrayList<String> data;
    private int cursor;
    
    public EZFileRead(String filename) {
        data = new ArrayList<String>();
        file = filename;
        isOpen = false;
        openRead();
        String t = readLine();
        while(t != null) { // Read until there are no more lines
            data.add(t);
            t = readLine();
        }
        close();
        cursor = 0;
    }
    
    /* Open a file for reading, if it exists */
    private void openRead() {
        if(isOpen) return;
        if(doesFileExist(file) == false) return;
        try {
            in = new BufferedReader(new FileReader(file));
        } catch (FileNotFoundException e) {
            isOpen = false;
            return;
        }
        isOpen = true;
    }
    
    /* Read in a line from file to a string */
    private String readLine() {
        if(!isOpen) return null;
        try {
            return in.readLine();
        } catch (IOException ex) {
            return null;
        }
    }
    
    /* Closes a file */
    private void close() {
        if(!isOpen) return;
        try {
            in.close();
        } catch (IOException e) {}
        isOpen = false;
    }
    
    /* Get the number of lines */
    public int getNumLines() {
        return data.size();
    }
    
    /* Get a specific line from file */
    public String getLine(int index) {
        if(index < 0 || index >= data.size()) return "NOT VALID INDEX!";
        return data.get(index);
    }
    
    /* Get next line based on a cursor */
    public String getNextLine() {
        if(cursor >= data.size()) return "END OF FILE";
        String ret = data.get(cursor);
        cursor++;
        return ret;
    }
    
    /* Check to see if a filename exists */
    public static boolean doesFileExist(String filename) {
        try {
            BufferedReader in2 = new BufferedReader(new FileReader(filename));
            in2.close();
            return true;
        } catch(IOException e) {
            return false;
        }
    }
}
