textures/skies/qznebula_bst
{
    qer_editorimage textures/skies/qznebula3.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm sky
	surfaceparm nodlight
	q3map_sunExt 1 1 1 15 0 90 0.5 32
	q3map_skylight 15 6
	q3map_lightmapSampleSize 32
	skyparms textures/skies/env/qznebula3 - -
}

textures/base_wall/glass02_solid
{
	qer_editorimage textures/base_wall/shiny3.tga
	cull none
	{
		map textures/effects/tinfx3.tga
		tcgen environment
		tcmod scale 0.85 0.85
		blendfunc add
		rgbgen identity
	}
	{
		map $lightmap
		rgbgen identity
		blendfunc filter
	}
}

textures/sfx/fan_terminatria
{
	surfaceparm trans
	surfaceparm nomarks
	cull none
	nopicmip
	qer_editorimage textures/bst_tech/fan_grey_ed.tga
	{
		clampmap textures/bst_tech/fan_grey.tga
		tcMod rotate 256 
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/bst_tech/bst_clangdark_bounce
{
	surfaceparm nodamage
	q3map_lightimage textures/bst_tech/bst_jumppadsmall.tga	
	q3map_surfacelight 400
	qer_editorimage textures/sfx/clangdark_bounce.tga

	
	{
		map textures/sfx/clangdark_bounce.tga
		rgbGen identity
	}
	
	{
		map $lightmap
		rgbGen identity
		blendfunc gl_dst_color gl_zero
	}
	
	{
		map textures/sfx/bouncepad01b_layer1.tga
		blendfunc gl_one gl_one
		rgbGen wave sin .5 .5 0 1.5	
	}

	{
		clampmap textures/bst_tech/bst_jumppadsmall.tga
		blendfunc gl_one gl_one
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave square .5 .5 .25 1.5
	}
}

textures/bst_tech/greywall_dark_s
{
	qer_editorimage textures/bst_tech/greywall_dark1.tga
	{
		map textures/effects/tinfx.tga
		rgbGen identity
		tcGen environment 
	}
	{
		map textures/bst_tech/greywall_dark1.tga
		blendfunc gl_src_alpha gl_one_minus_src_color
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc gl_dst_color gl_one_minus_dst_alpha
		rgbGen identity
		tcGen lightmap 
	}
}


textures/bst_tech/bst_striplight_1k
{
	qer_editorimage textures/bst_tech/bst_striplight.tga
	q3map_lightimage textures/bst_tech/bst_striplight.tga
	surfaceparm nomarks
	q3map_surfacelight 1000

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_striplight.tga
		rgbGen identity
	}
}

textures/bst_tech/bst_striplight2_1000
{
	qer_editorimage textures/bst_tech/bst_striplight3.tga
	q3map_lightimage textures/bst_tech/bst_striplight3.tga
	surfaceparm nomarks
	q3map_surfacelight 1000

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_striplight3.tga
		rgbGen identity
	}
}

textures/bst_tech/bst_striplight2_250
{
	qer_editorimage textures/bst_tech/bst_striplight2.tga
	q3map_lightimage textures/bst_tech/bst_striplight2.tga
	surfaceparm nomarks
	q3map_surfacelight 250

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_striplight2.tga
		rgbGen identity
	}
}

textures/bst_tech/bst_ventlight_1k
{
	qer_editorimage textures/bst_tech/bst_vent7.tga
	surfaceparm nomarks
	q3map_surfacelight 1000

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_ventlight_500
{
	qer_editorimage textures/bst_tech/bst_vent7.tga
	surfaceparm nomarks
	q3map_surfacelight 500

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_ventlight_250
{
	qer_editorimage textures/bst_tech/bst_vent7.tga
	surfaceparm nomarks
	q3map_surfacelight 250

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_vent7_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_trim_sml_2k
{
	qer_editorimage textures/bst_tech/bst_trim_sml.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	q3map_lightSubdivide 64

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_sml.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_sml_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_trim_s3_2k
{
	qer_editorimage textures/bst_tech/bst_trim_s3.tga
	surfaceparm nomarks
	q3map_surfacelight 2000
	q3map_lightSubdivide 64

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_trim_s3_1k
{
	qer_editorimage textures/bst_tech/bst_trim_s3.tga
	surfaceparm nomarks
	q3map_surfacelight 1000
	q3map_lightSubdivide 64

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_trim_s3_500
{
	qer_editorimage textures/bst_tech/bst_trim_s3.tga
	surfaceparm nomarks
	q3map_surfacelight 500
	q3map_lightSubdivide 64

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

textures/bst_tech/bst_trim_s3_250
{
	qer_editorimage textures/bst_tech/bst_trim_s3.tga
	surfaceparm nomarks
	q3map_surfacelight 500
	q3map_lightSubdivide 64

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/bst_tech/bst_trim_s3_blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

// ITEM MARKERS

textures/bst_tech/bst_teleexit_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_teleexit.tga
      nopicmip
   {
      map textures/bst_tech/bst_teleexit.tga
   }
}

textures/bst_tech/bst_item_ar_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_item_ar.tga
      nopicmip
   {
      map textures/bst_tech/bst_item_ar.tga
   }
}

textures/bst_tech/bst_item_mh_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_item_mh.tga
      nopicmip
   {
      map textures/bst_tech/bst_item_mh.tga
   }
}

textures/bst_tech/bst_weap_sg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_sg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_sg.tga
   }
}

textures/bst_tech/bst_weap_pg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_pg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_pg.tga
   }
}

textures/bst_tech/bst_weap_gl_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_gl.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_gl.tga
   }
}

textures/bst_tech/bst_weap_rl_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_rl.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_rl.tga
   }
}

textures/bst_tech/bst_weap_lg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_lg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_lg.tga
   }
}

textures/bst_tech/bst_weap_rg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_rg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_rg.tga
   }
}

//red markers


textures/bst_tech/bst_item_red_ar_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_item_red_ar.tga
      nopicmip
   {
      map textures/bst_tech/bst_item_red_ar.tga
   }
}

textures/bst_tech/bst_item_red_mh_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_item_red_mh.tga
      nopicmip
   {
      map textures/bst_tech/bst_item_red_mh.tga
   }
}

textures/bst_tech/bst_weap_red_sg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_sg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_sg.tga
   }
}

textures/bst_tech/bst_weap_red_pg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_pg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_pg.tga
   }
}

textures/bst_tech/bst_weap_red_gl_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_gl.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_gl.tga
   }
}

textures/bst_tech/bst_weap_red_rl_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_rl.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_rl.tga
   }
}

textures/bst_tech/bst_weap_red_lg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_lg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_lg.tga
   }
}

textures/bst_tech/bst_weap_red_rg_nm
{
      surfaceparm nomarks
      qer_editorimage textures/bst_tech/bst_weap_red_rg.tga
      nopicmip
   {
      map textures/bst_tech/bst_weap_red_rg.tga
   }
}