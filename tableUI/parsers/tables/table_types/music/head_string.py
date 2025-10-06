SONGLIST_HEAD_STRING = r'''
/// @file   mmMusic.tbl
/// @brief  MMAllOutによる自動出力
/// @author Tsuyoshi Araya
/// @date   2019/04/03 10:55:36
/// @note   Output by MMAllOutVer 0.12(13/02/19)
///
/// Copyright(C)SEGA


#define MMMUSIC_TBL

#if 0
/// @brief Musicのテーブル
struct SMusic{
    ID       ID;
    NAME     enum;
    DATA     Ver;
    DATA     SubCate;
    DATA     BPM;
    DATA     SortID;
    DATA     ドレス;
    DATA     暗黒;
    DATA     mile;
    DATA     VL;
    DATA     Event;
    DATA     Rec;
    DATA     PVStart;
    DATA     PVEnd;
    DATA     曲長さ;
    DATA     オフRanking;
    DATA     AD Def;
    DATA     ReMaster;
    DATA     特殊PV;
    DATA     チャレンジトラック;
    DATA     ボーナス;
    DATA     GenreID;
    DATA     タイトル;
    DATA     アーティスト;
    DATA     sort_jp_index;
    DATA     sort_ex_index;
    TEXT     filename;
};
#endif //0

/// @brief Musicのテーブルリスト
'''.strip()
