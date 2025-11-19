
textures/map_sinister/sinister_sky
{
	qer_trans 0.60
	qer_editorimage textures/skies/cannery_blueclouds.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky

	q3map_sun 0.4 0.666667 0.8 85 180 80
	//q3map_sun 0.4 0.666667 0.8 85 315 80
	q3map_surfacelight 120
	q3map_lightimage textures/skies/toxicsky.tga
	q3map_lightsubdivide 512

	skyparms - 512 -
	{
		map textures/skies/cannery_dimclouds.tga
		tcMod scale 3 2
		tcMod scroll 0.015 0.015
		depthWrite
	}
	{
		map textures/skies/cannery_blueclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 3 3
		tcMod scroll 0.01 0.01
	}
}

textures/map_sinister/item_decal_armor_sand
{
	qer_editorimage textures/map_sinister/item_decal_armor_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_armor_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_armor.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_gl_sand
{
	qer_editorimage textures/map_sinister/item_decal_gl_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_gl_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_gl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_lg_sand
{
	qer_editorimage textures/map_sinister/item_decal_lg_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_lg_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_lg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_mh_sand
{
	qer_editorimage textures/map_sinister/item_decal_mh_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_mh_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_mh.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_ng_sand
{
	qer_editorimage textures/map_sinister/item_decal_ng_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_ng_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_ng.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_pg_sand
{
	qer_editorimage textures/map_sinister/item_decal_pg_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_pg_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_pg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_quad_sand
{
	qer_editorimage textures/map_sinister/item_decal_quad_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_quad_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_quad.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_rg_sand
{
	qer_editorimage textures/map_sinister/item_decal_rg_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_rg_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_rl_sand
{
	qer_editorimage textures/map_sinister/item_decal_rl_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_rl_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_rl.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}

textures/map_sinister/item_decal_sg_sand
{
	qer_editorimage textures/map_sinister/item_decal_sg_sand.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	cull none
	nopicmip
	novlcollapse
	polygonOffset 
	sort 6
	{
		map textures/map_sinister/item_decal_sg_sand.tga
		blendfunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc filter
		depthFunc equal
	}
	{
		map textures/se_gothic/item_decal_sg.blend.tga
		rgbGen wave sin 0 .5 0 .25
		blendfunc add
	}
}


textures/map_sinister/orange_flare
{
	surfaceparm trans	
	surfaceparm nomarks	
	surfaceparm nonsolid
	surfaceparm nolightmap
	cull none
	nopicmip
	{
		map textures/map_sinister/orange_flare.tga
		tcMod Scroll .3 0
		blendfunc add
	}
}

textures/map_sinister/tp_darkwood_singleplank
{
	surfaceparm	woodsteps
	q3map_forceMeta
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/map_sinister/tp_darkwood_singleplank.tga
		blendfunc filter
	}
}