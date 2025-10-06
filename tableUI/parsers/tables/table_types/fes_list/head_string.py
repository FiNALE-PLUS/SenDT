FESLIST_HEAD_STRING = r'''
/// @file   mmFesList.tbl
/// @brief  MMAllOutによる自動出力
/// @author Tsuyoshi Araya
/// @date   2019/06/26 15:12:05
/// @note   Output by MMAllOutVer 0.12(13/02/19)
///
/// Copyright(C)SEGA


#define MMFESLIST_TBL

#if 0
/// @brief FesListのテーブル
struct SFesList{
    NAME     名前;
    DATA     ID;
    DATA     EVENT;
    DATA     SordID;
    DATA     ScoreID;
    DATA     Dif;
    DATA     Creator;
    DATA     Mirror;
    DATA     Disp;
    DATA     Skip;
    DATA     Judge;
    DATA     RstCommentID;
};
#endif //0

/// @brief FesListのテーブルリスト
'''.strip()
