package api;

import org.json.JSONObject;

public class ConfigurationManager {
    private boolean m_isSpeedDropEnabled = true;
    private boolean m_isSkipCopyright = true;
    private boolean m_isSkipLevelPick = true;
    private boolean m_applyDeathScreenPatch = true;
    private boolean m_skipTitleDemoScreens = true;
    private boolean m_isAsync = false;
    private boolean m_isDebug = true;
    private String m_aiURL = "http://localhost:8080/ai";
    private boolean m_startOver = true;
    private boolean m_skipClearAnimation = true;
    private ConfigurationManager(){

    }
    public static ConfigurationManager fromJson(JSONObject data){
        ConfigurationManager manager = new ConfigurationManager();
        if (data == null){
            return manager;
        }
        manager.m_isSpeedDropEnabled = data.optBoolean("speed_drop", manager.m_isSpeedDropEnabled);
        manager.m_isSkipCopyright = data.optBoolean("skip_copyright", manager.m_isSkipCopyright);
        manager.m_isSkipLevelPick = data.optBoolean("skip_level_pick", manager.m_isSkipLevelPick);
        manager.m_applyDeathScreenPatch = data.optBoolean("apply_death_screen_patch", manager.m_applyDeathScreenPatch);
        manager.m_skipTitleDemoScreens = data.optBoolean("skip_title_demo_screens", manager.m_skipTitleDemoScreens);
        manager.m_aiURL = data.optString("ai_url", manager.m_aiURL);
        manager.m_isAsync = data.optBoolean("is_async", manager.m_isAsync);
        manager.m_isDebug = data.optBoolean("is_debug", manager.m_isDebug);
        manager.m_startOver = data.optBoolean("start_over", manager.m_startOver);
        Logger.getInstance().log("Received config: " + data);

        return manager;
    }

    public boolean isSpeedUpDropEnabled(){
        return this.m_isSpeedDropEnabled;
    }
    public boolean isSkipCopyright(){
        return this.m_isSkipCopyright;
    }
    public boolean isSkipLevelPick(){
        return this.m_isSkipLevelPick;
    }
    public boolean isApplyDeathScreenPatchEnabled(){
        return this.m_applyDeathScreenPatch;
    }
    public boolean isStartOver() {return m_startOver;}
    public boolean isSkipTitleDemoScreens(){
        return this.m_skipTitleDemoScreens;
    }
    public String getAIUrl(){
        return this.m_aiURL;
    }
    public boolean isAsync(){
        return this.m_isAsync;
    }
    public boolean isDebug(){
        return  this.m_isDebug;
    }
    public boolean isSkipClearAnimation() {return m_skipClearAnimation;}
}
