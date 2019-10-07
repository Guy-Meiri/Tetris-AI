package api;

public class Utils {
    public static int parsebcdByte(int data, int defaultValue) {
        data = data & 0xff;
        byte low = (byte) (data & 0xf);
        byte high = (byte)(((data & 0xf0 ) >>> 4) & 0xf);
        if (low >= 10 || (high) >= 10){
            return defaultValue;
        }
        return low + high * 10;
    }
}
