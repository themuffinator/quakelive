models/mapobjects/mrc_tele2/mrc5_portal_red
{ 
	qer_editorimage models/mapobjects/mrc_tele2/mrc5_portal_red.tga
	surfaceparm nomarks
    surfaceparm trans
	surfaceparm nonsolid
	q3map_lightimage models/mapobjects/mrc_tele2/mrc5_portal_red.tga
	q3map_surfacelight 300
	q3map_lightsubdivide 32
    sort additive	
	
        {	        
	        map models/mapobjects/mrc_tele2/mrc5_portal_red.tga
			blendFunc add
            tcmod rotate 75
		}
}

models/mapobjects/mrc_tele2/mrc5_portal_blue
{ 
	qer_editorimage models/mapobjects/mrc_tele2/mrc5_portal_blue.tga
	surfaceparm nomarks
    surfaceparm trans
	surfaceparm nonsolid
	q3map_lightimage models/mapobjects/mrc_tele2/mrc5_portal_blue.tga
	q3map_surfacelight 300
	q3map_lightsubdivide 32
    sort additive	
	
        {	        
	        map models/mapobjects/mrc_tele2/mrc5_portal_blue.tga
			blendFunc add
            tcmod rotate 75
		}
}
models/mapobjects/mrc_tele2/mrc5_portal_green
{ 
	qer_editorimage models/mapobjects/mrc_tele2/mrc5_portal_green.tga
	surfaceparm nomarks
    surfaceparm trans
	surfaceparm nonsolid
	q3map_lightimage models/mapobjects/mrc_tele2/mrc5_portal_green.tga
	q3map_surfacelight 300
	q3map_lightsubdivide 32
    sort additive	
	
        {	        
	        map models/mapobjects/mrc_tele2/mrc5_portal_green.tga
			blendFunc add
            tcmod rotate 75
		}
}

models/mapobjects/mrc_tele2/mrc5_portal_tourney
{ 
	qer_editorimage models/mapobjects/mrc_tele2/mrc5_portal_tourney.tga
	surfaceparm nomarks
    surfaceparm trans
	surfaceparm nonsolid
	q3map_lightimage models/mapobjects/mrc_tele2/mrc5_portal_tourney.tga
	q3map_surfacelight 300
	q3map_lightsubdivide 32
    sort additive	
	
        {	        
	        map models/mapobjects/mrc_tele2/mrc5_portal_tourney.tga
			blendFunc add
            tcmod rotate 75
		}
}

models/mapobjects/mrc_tele2/mrc4_light_02
{
	qer_editorimage models/mapobjects/mrc_tele2/mrc4_light_02.tga
	q3map_lightimage models/mapobjects/mrc_tele2/mrc4_light_02.blend.tga
	q3map_surfacelight 100
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map models/mapobjects/mrc_tele2/mrc4_light_02.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map models/mapobjects/mrc_tele2/mrc4_light_02.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}