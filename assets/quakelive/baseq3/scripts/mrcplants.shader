
models/mapobjects/mrcplants/leaf01
{
	cull none

	surfaceparm alphashadow
	surfaceparm pointlight
	surfaceparm trans

	qer_editorImage models/mapobjects/mrcplants/leaf01.tga
	qer_alphaFunc gequal 0.5

	{
		map models/mapobjects/mrcplants/leaf01.tga
		rgbGen vertex
		alphaGen const 1.0
		alphaFunc GE128
		depthWrite
	}
}

models/mapobjects/mrcplants/grass01
{
	cull none

	surfaceparm alphashadow
	surfaceparm pointlight
	surfaceparm trans

	qer_editorImage models/mapobjects/mrcplants/grass01.tga
	qer_alphaFunc gequal 0.5

	{
		map models/mapobjects/mrcplants/grass01.tga
		rgbGen vertex
		alphaGen const 1.0
		alphaFunc GE128
		depthWrite
	}
}

models/mapobjects/mrcplants/ivy01
{
	cull none

//	surfaceparm alphashadow
	surfaceparm pointlight
	surfaceparm trans

	qer_editorImage models/mapobjects/mrcplants/ivy01.tga
	qer_alphaFunc gequal 0.5

	{
		map models/mapobjects/mrcplants/ivy01.tga
		rgbGen vertex
		alphaGen const 1.0
		alphaFunc GE128
		depthWrite
	}
}