SCORE_LIST_HEAD_STRING = r'''
/// @file   mmScore.tbl
/// @brief  MMAllOutによる自動出力
/// @author Tsuyoshi Araya
/// @date   2019/06/26 10:42:33
/// @note   Output by MMAllOutVer 0.12(13/02/19)
///
/// Copyright(C)SEGA


#define MMSCORE_TBL

#if 0
/// @brief Scoreのテーブル
struct SScore{
    ID       ID;
    NAME     enum;
    DATA     LV;
    DATA     譜面作者ID;
    DATA     計算対象;
    TEXT     safename;
};
#endif //0

/// @brief Scoreのテーブルリスト
'''.strip()
