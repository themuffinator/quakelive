models/mapobjects/gratelamp/gratelight
{
	surfaceparm trans
	{
		map models/mapobjects/gratelamp/gratelight.tga
		blendfunc blend
		rgbgen vertex
	}
}

models/mapobjects/gratelamp/lightbulb
{
	surfaceparm trans
	{
		map models/mapobjects/gratelamp/lightbulb.tga
		tcgen environment
		blendfunc add
		rgbgen identity
	}
}

models/mapobjects/gratelamp/gratelight_flare
{
	deformvertexes autosprite
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none
	{
		map models/mapobjects/gratelamp/gratelight_flare.tga
		blendfunc add
		rgbgen wave sin .5 .2 0 0
	}
}