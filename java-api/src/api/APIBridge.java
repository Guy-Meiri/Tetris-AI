package api;

import nintaco.api.*;
import org.json.*;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.lang.management.ManagementFactory;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Iterator;

public class APIBridge {
    private final String CONFIG_URL = "http://localhost:8080/config";
    private final API api = ApiSource.getAPI();
    private GameStateManager m_game_param_extractor = null;
    private InformationProvider m_provider;
    private long update_id = 0;
    private long session_id = 0;
    private ConfigurationManager m_configManager = null;

    public ControllersListener onFrameRenderedListener = new ControllersListener () {
        public void controllersProbed() {
            if (!m_game_param_extractor.isPlaying()){
                m_game_param_extractor.skipTillPlaying(m_configManager.isSkipCopyright(),
                        m_configManager.isSkipTitleDemoScreens(),
                        m_configManager.isSkipLevelPick());
                return;
            }
            if (m_configManager.isSkipClearAnimation()) {
                m_game_param_extractor.skipClearingAnimation();
            }
            boolean hasUpdated = m_provider.updateValues();
            if (m_configManager.isStartOver() && m_provider.hasGameEnded()){
                m_game_param_extractor.pressStart();
                if (update_id != 0){
                    inform(hasUpdated);
                    update_id = 0;
                    session_id += 1;
                    m_provider = InformationProvider.forceNewInstance();
                }
                return;
            }

            inform(hasUpdated);
            return;
        }
    };

    private void inform(boolean hasUpdated){
        if (!hasUpdated){
            return;
        }
        if (m_configManager.isAsync()) {
            informAndTakeActionAsync();
        } else {
            informAndTakeActionSync(true);
        }
    }

    public static String getPID(){
        String name = ManagementFactory.getRuntimeMXBean().getName();
        String pid = name.substring(0, name.indexOf("@"));
        return pid;
    }

    public void informAndTakeActionSync(boolean incUpdateID){
        Logger.getInstance().log("Sending request");
        JSONObject data = m_provider.intoJSON();
        data.put("update_id", update_id);
        data.put("session_id", session_id);
        data.put("pid", getPID());
        if (incUpdateID){
            update_id++;
        }
        JSONObject action = syncPostRequest(data, m_configManager.getAIUrl());
        takeAction(action);
    }

    public void informAndTakeActionAsync(){
        synchronized (this){
            long seq_id = update_id;
            Thread th = new Thread(() -> {
                informAndTakeActionSync(false);
            });
            update_id++;
            th.start();
        }
    }

    private ConfigurationManager getConfigurationManager(){
        JSONObject obj = new JSONObject();
        Logger logger = Logger.getInstance();
        JSONObject resp = syncPostRequest(obj, CONFIG_URL);
        int sleepTime = 200;
        while (resp == null){
            logger.log("Config fetching failed, polling on server...");
            try {
                Thread.sleep(sleepTime);
            } catch (InterruptedException e){}
            resp = syncPostRequest(obj, CONFIG_URL, false);
            sleepTime = sleepTime * 2;
            if (sleepTime > 3000) { //if we wait longer then 3 seconds
                sleepTime = 3000;
            }
        }
        return ConfigurationManager.fromJson(resp);
    }

    public void launch(){
        m_provider = InformationProvider.getInstance();
        api.addControllersListener(this.onFrameRenderedListener);
        m_game_param_extractor = GameStateManager.getInstance();
        m_configManager = getConfigurationManager();
        Logger.init(m_configManager);
        if (m_configManager.isApplyDeathScreenPatchEnabled()){
            m_game_param_extractor.applyDeathScreenFix();
        }
        if (m_configManager.isSpeedUpDropEnabled()){
            m_game_param_extractor.applyDropSpeedUpPatch();
        }
        api.run();
    }
    private int keyToGamepadButton(String key){
        if (key.toLowerCase().equals("up")){
            return GamepadButtons.Up;
        }
        if (key.toLowerCase().equals("none") || key.toLowerCase().equals("down")){
            return GamepadButtons.Down;
        }
        if (key.toLowerCase().equals("left")){
            return GamepadButtons.Left;
        }
        if (key.toLowerCase().equals("right")){
            return GamepadButtons.Right;
        }
        if (key.toLowerCase().equals("a")){
            return GamepadButtons.A;
        }
        if (key.toLowerCase().equals("b")){
            return GamepadButtons.B;
        }
        return -1;
    }

    private void takeAction(JSONObject actions){
        //TODO: for some reason the down pressing does not cause a speed drop
        //      of the tetrimino, we should fix that to save time.
        if (actions == null){
            return;
        }
        Iterator<Object> keys = actions.getJSONArray("keys").iterator();
        Logger logger = Logger.getInstance();
        while (keys.hasNext()){
            Object data = keys.next();
            if (!(data instanceof String)){
                logger.log("Received non string data - " + (data));
                continue;
            }
            String key = (String)data;
            int gamepadButton = keyToGamepadButton(key);
            if (gamepadButton == -1){
                logger.log("unknown key received '" + key + "'");
                continue;
            }
            logger.log("Pressing '" + key + "'");
            api.writeGamepad(0, gamepadButton, true);
        }
    }

    public static JSONObject syncPostRequest(JSONObject data, String url) {
        return syncPostRequest(data, url, true);
    }

    public static JSONObject syncPostRequest(JSONObject data, String url, boolean isPrint){
        BufferedReader reader = null;
        DataOutputStream ostream = null;
        JSONObject result = null;
        try {
            URL newUrl = new URL(url);
            HttpURLConnection con = (HttpURLConnection) newUrl.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            con.setDoOutput(true);
            con.setConnectTimeout(1000); // 1 seconds
            con.connect();
            ostream = new DataOutputStream(con.getOutputStream());
            ostream.write(data.toString().getBytes("UTF-8"));
            ostream.flush();
            ostream.close();

            //consume the input stream for reuse
            InputStream inputStream = con.getInputStream();
            JSONTokener jsonTokener = new JSONTokener(inputStream);
            result = new JSONObject(jsonTokener);

        } catch (Exception e){
            if (isPrint){
                e.printStackTrace();
                System.out.println(data);
            }
        } finally {
            return result;
        }
    }

    public static final void main(final String... args){
        Logger.getInstance().log("Running!");
        new APIBridge().launch();

    }
}
