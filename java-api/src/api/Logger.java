package api;

public class Logger {
    private static Logger m_instance = null;
    private static ConfigurationManager m_configManager = null;
    private Logger(){}
    public static void init(ConfigurationManager manager){
        m_configManager = manager;
    }
    public static Logger getInstance() {
        if (m_instance == null){
            m_instance = new Logger();
        }
        return m_instance;
    }

    public void log(String logmsg){
        if (m_configManager != null && !m_configManager.isDebug()){
            return;
        }
        System.out.println("[LOG] " + logmsg);
    }
}
