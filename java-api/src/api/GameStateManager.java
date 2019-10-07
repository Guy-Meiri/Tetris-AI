package api;

import nintaco.api.*;

public class GameStateManager {
    private final API m_api = ApiSource.getAPI();
    private int m_startCounter = 0;
    private boolean m_hasAppliedScoreFix = false;
    private boolean m_hasAppliesDropSpeedUpPatch = false;
    private static GameStateManager m_instance = null;


    public static GameStateManager getInstance() {
        if (m_instance == null){
            m_instance = new GameStateManager();
        }

        return m_instance;
    }
    public void skipCopyrightScreen(int gameState){
        if (gameState != GameState.LEGAL_SCREEN) {
            return;
        }
        if (m_api.peekCPU(Addresses.COPYRIGHT1) > 1){
            m_api.writeCPU(Addresses.COPYRIGHT1, 0);
        }
        if (m_api.peekCPU(Addresses.COPYRIGHT2) > 2){
            m_api.writeCPU(Addresses.COPYRIGHT2, 1);
        }
    }

    public void pressStart(){
        m_startCounter++;
        if (m_startCounter % 10 != 0){
            return;
        }
        m_startCounter = 0;
        Logger.getInstance().log("pressing enter");
        m_api.writeGamepad(0, GamepadButtons.Start, true);
    }

    public void skipTillPlaying(boolean skipCopyright, boolean skipTitleAndDemo, boolean skipGamePick){
        int gameState = m_api.peekCPU(Addresses.GAME_STATE);
        if (gameState == GameState.PLAY_HIGHSCORE_ENDING_PAUSE){
            return;
        }
        if (skipCopyright){
            skipCopyrightScreen(gameState);
        }
        if (skipTitleAndDemo){
            skipTitleAndDemoScreens(gameState);
        }
        resetPlayState(gameState);
        if (skipGamePick){
            pressStart();
        }
    }
    public void skipTitleAndDemoScreens(int gameState){
        if (gameState == GameState.TITLE_SCREEN || gameState == GameState.DEMO_SCREEN) {
            pressStart();
        }
    }


    public void applyDeathScreenFix(){
        if (m_hasAppliedScoreFix){
            return;
        }
        m_api.addAccessPointListener((int type, int address, int value) -> {
            int pointsMul = m_api.peekCPU(0x00A8);
            if (pointsMul > 30){
                m_api.writeCPU(0x00A8, 30);
            }
            return -1;
        }, AccessPointType.PreExecute, Addresses.SCORE_BUG_FUNC);
        m_hasAppliedScoreFix = true;
    }

    public void applyDropSpeedUpPatch(){
        if (m_hasAppliesDropSpeedUpPatch){
            return;
        }
        m_api.addAccessPointListener((int type, int address, int value) -> {
            m_api.setX(0x1E);
            return -1;
        }, AccessPointType.PreExecute, Addresses.SPEED_UP_DROP);
    }
    public void skipClearingAnimation(){
        int playState = m_api.peekCPU(Addresses.PLAY_STATE);
        if (playState != 4){
            return;
        }
        m_api.writeCPU(Addresses.PLAY_STATE, 5);
    }
    public void resetPlayState(int gameState){
        if (gameState == GameState.PLAY_HIGHSCORE_ENDING_PAUSE){
            return;
        }
        m_api.writeCPU(Addresses.PLAY_STATE, 0);
    }
    public boolean isPlaying(){
        return m_api.peekCPU(Addresses.GAME_STATE) == GameState.PLAY_HIGHSCORE_ENDING_PAUSE;
    }
}
