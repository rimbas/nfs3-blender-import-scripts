#include <std/string.pat>

struct FloatPT {
    float x [[color("990000")]];
    float z [[color("000099")]];
    float y [[color("009900")]];
} [[static]];

struct IntPT {
    s32 x [[color("990000")]];
    s32 z [[color("000099")]];
    s32 y [[color("009900")]];
} [[static]];

struct PolygonData {
    u16 vertex[4];
    u16 textureId;
//    u16 unknown1;
    padding[2]; // unknown
    u8 flags;
    //u8 unknown2;
    padding[1]; // unknown
} [[static]];

struct NeighborData {
    s16 block;
    padding[2]; // unknown
} [[static]];

struct PositionData {
    u16 polygon;
    u8 polygonCount;
    padding[1]; //unknown
    s16 extraNeighbor[2];
} [[static]];

struct PolyVroadData {
    u8 vroadEntry;
    u8 flags;
    padding[6]; // unknown
} [[static]];

struct VroadData {
    s16 xNorm [[color("990000")]];
    s16 zNorm [[color("000099")]];
    s16 yNorm [[color("009900")]];
    s16 xForw [[color("990000")]];
    s16 zForw [[color("000099")]];
    s16 yForw [[color("009900")]];    
} [[static]];

struct RefXObj {
    IntPT point;
    padding[2]; // unknown
    s16 globalno;
    padding[2]; // unknown
    s8 crossindex;
    padding[1]; // unknown
} [[static]];

struct RefPolyObj {
    s16 entrySize;
    u8 type;
    u8 number;
    IntPT point;
    s32 crossindex;
} [[static]];

struct Soundsrc {
    IntPT point;
    s32 type;
} [[static]];

struct Lightsrc {
    IntPT point;
    s32 type;
} [[static]];

struct TrackBlock {
    FloatPT center;
    FloatPT bounding[4];
    u32 vertexCount;
    u32 hiResVertexCount;
    u32 lowResVertexCount;
    u32 medResVertexCount;
    u32 vertexCountDuplicate;
    u32 nObjectVert;
    FloatPT vertices[vertexCount];
    s32 shadingVertices[vertexCount];
    NeighborData neighborData[0x12C];
    s32 startPosition;
    s32 nPositions;
    s32 nPolygons;
    s32 nVroad;
    s32 nXobj;
    s32 nPolyObj;
    s32 nSoundsrc;
    s32 nLightsrc;
    PositionData posData[nPositions];
    PolyVroadData polyData[nPolygons];
    VroadData vroadData[nVroad];
    RefXObj xobj[nXobj];
    RefPolyObj polyobj[nPolyObj];
//    padding[nPolyObj % 20];
    Soundsrc soundsrc[nSoundsrc];
    Lightsrc lightsrc[nLightsrc];
};

struct PolygonChunk {
    s32 size;
    padding[4]; // duplicate size
    PolygonData poly[size];
};

struct PolyObjData {
    s32 type;
    if (type == 1) {
        s32 numpoly;
        PolygonData poly[numpoly];
    }
};

struct ObjPolyBlock {
    s32 nPolygons;
    s32 nObjects;
    PolyObjData obj[nObjects];
};

struct PolygonBlock {
    PolygonChunk poly[7];
    ObjPolyBlock obj[4];
};


struct XobjData {
    s32 type;
    s32 crossno;
    padding[4]; // unknown
    FloatPT pointRef;
    padding[4]; // unknown
    u32 nVertices;
    FloatPT vert[nVertices];
    u32 shadingVertices[nVertices];
    u32 nPolygons;
    PolygonData polyData[nPolygons];
};

struct XobjBlock {
    u32 nobj;
    XobjData obj[nobj];
};

struct TextureBlock {
    u16 width;
    u16 height;
    padding[4]; // unknown
    float corners[8];
    padding[4]; // unknown
    char islane;
    s16 texture;
} [[static]];

struct FrdFile {
    padding[28];
    s32 nBlocks;
    TrackBlock track[1];
/*    TrackBlock track[nBlocks+1];
    PolygonBlock poly[nBlocks+1];
    XobjBlock xobj[4*(nBlocks+1)+1];
    s32 nTextures;
    TextureBlock texture[nTextures];
    */
};


FrdFile frd @ 0x00;



