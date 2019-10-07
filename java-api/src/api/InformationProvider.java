package api;

import nintaco.api.API;
import nintaco.api.ApiSource;
import org.json.JSONArray;
import org.json.JSONObject;

public class InformationProvider {
    private final API m_api = ApiSource.getAPI();
    private static InformationProvider m_instance = null;
    private int m_TetriminoX = 0;
    private int m_TetriminoY = 0;
    private int m_level = 0;
    private int m_score1 = 0;
    private int m_score2 = 0;
    private int m_score3 = 0;
    private int m_total_score = 0;
    private int m_tetriminoID = 0;
    private int m_nextTetriminoID = 0;
    private boolean m_hasGameEnded = false;
    private int[][] m_board = new int[20][10];

    public boolean updateValues(){
        boolean hasChanged = false;
        int temp = 0;
        temp = m_api.peekCPU(Addresses.TetriminoX);
        if (temp != m_TetriminoX){
            hasChanged = true;
            m_TetriminoX = temp;
        }
        temp = m_api.peekCPU(Addresses.TetriminoY);
        if (temp != m_TetriminoY){
            hasChanged = true;
            m_TetriminoY = temp;
        }

        temp = getScore();
        if (temp != m_total_score){
            hasChanged = true;
            m_total_score = temp;
        }
        boolean ended = (m_api.peekCPU(0x48) == 0xa);
        if (ended != m_hasGameEnded){
            hasChanged = true;
            m_hasGameEnded = ended;
        }
        temp = m_api.peekCPU(Addresses.TETRIMINO_ID);
        if (temp != m_tetriminoID){
            hasChanged = true;
            m_tetriminoID = temp;
        }

        temp = m_api.peekCPU(Addresses.NEXT_TETRIMINO_ID);
        if (temp != m_nextTetriminoID){
            hasChanged = true;
            m_nextTetriminoID = temp;
        }
        readBoard();
        m_level = m_api.peekCPU(Addresses.LEVEL);
        return hasChanged;
    }

    public boolean hasGameEnded(){
        return m_hasGameEnded;
    }
    private int getScore(){
        m_score1 = Utils.parsebcdByte(m_api.peekCPU(Addresses.SCORE1), m_score1);
        m_score2 = Utils.parsebcdByte(m_api.peekCPU(Addresses.SCORE2), m_score2);
        m_score3 = Utils.parsebcdByte(m_api.peekCPU(Addresses.SCORE3), m_score3);
        return m_score3*10000 + m_score2*100 + m_score1;
    }

    private void readBoard(){
        for (int i = 0; i < 20; i++){
            for (int j = 0; j < 10; j++){
                m_board[i][j] = m_api.peekCPU(Addresses.PLAY_BOARD+ i*10 + j);
            }
        }
    }

    public JSONObject intoJSON(){
        JSONObject state = new JSONObject();
        state.put("score", m_total_score);
        state.put("tetrimino_x", m_TetriminoX);
        state.put("tetrimino_y",m_TetriminoY);
        state.put("tetrimino_id", m_tetriminoID);
        state.put("next_tetrimino_id", m_nextTetriminoID);
        state.put("has_game_ended", m_hasGameEnded);
        state.put("board", new JSONArray(m_board));
        state.put("level", m_level);
        return state;
    }

    public static InformationProvider forceNewInstance(){
        m_instance = null;
        return InformationProvider.getInstance();
    }
    public static InformationProvider getInstance(){
        if (m_instance == null){
            m_instance = new InformationProvider();
        }
        return m_instance;
    }


}
