// q3map_sun <red> <green> <blue> <intensity> <degrees> <elevation>
// color will be normalized, so it doesn't matter what range you use
// intensity falls off with angle but not distance 100 is a fairly bright sun
// degree of 0 = from the east, 90 = north, etc.  altitude of 0 = sunrise/set, 90 = noon
//test sky with lightning
textures/map_qzdm2k4/qzdm2k4_sky
{
	qer_editorimage textures/skies/lightn_clouds2.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	q3map_surfacelight 96
	q3map_lightimage textures/common/white.tga
	skyparms - 512 -
	{
		map textures/skies/meth_clouds2.tga
		tcMod scale 10 10
		tcMod scroll .09 .09
		depthWrite
	}

	{
		animMap 2.1 textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds2.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga textures/skies/lightn_clouds1.tga
		blendfunc add
		rgbGen	wave sin 0.2 0.4 0 1.1
		tcMod scale 10 10
		tcMod scroll .09 .09
	}
	{
		map textures/skies/topclouds.tga
		blendfunc add
		tcMod scale 4 4
		tcMod scroll 0.07 0.07
	}
}

// smoothed rockwall
textures/map_qzdm2k4/brick01_01_shadeangle_120
{
	q3map_nonplanar
	q3map_shadeangle 120
	qer_editorimage textures/map_qzdm2k4/brick01_01_shadeangle_120.tga
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/shw/brick01_01.tga
		blendFunc filter
	}
}

textures/map_qzdm2k4/qzdm2k4_stainedglass_01
{
   qer_editorimage textures/phantgothic/phantgothic_stainedglass_002.tga
	
   surfaceparm lightfilter
   surfaceparm nolightmap

   cull disable

   q3map_lightmapFilterRadius 0 4
   q3map_surfacelight 100
}