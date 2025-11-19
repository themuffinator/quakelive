textures/phantq3ctf1/cautionstripes_trimmed_04
{
	qer_editorimage textures/base_trim/cautionstripes_trimmed_06.tga
	{
		map textures/base_trim/cautionstripes_trimmed_04.tga
		tcmod scale .25 .25
	}
}

//-------------------------- Rock

textures/phantq3ctf1/rocks_4
{
	qer_editorimage textures/phantq3ctf1/rocks_4.tga
	q3map_forcemeta
	q3map_nonplanar
	q3map_shadeAngle 40
	q3map_lightmapSampleOffset 8.0
	{
		map textures/phantq3ctf1/rocks_4.tga
		rgbGen identity
	}	
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

 
//-------------------------- SFX

textures/phantq3ctf1/phantq3ctf1_water
{
	qer_editorimage textures/phantq3ctf1/phantq3ctf1_water.tga
	qer_trans .9
	q3map_globaltexture
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm water	
	cull disable
	deformVertexes wave 64 sin .25 .25 0 .5	
	{ 
		map textures/liquids/pool3d_3e.tga
		blendFunc GL_dst_color GL_one
		rgbgen identity
		tcmod scale .5 .5
		tcmod scroll .025 .01
	}	
	{ 
		map textures/phantq3ctf1/phantq3ctf1_water.tga
		blendFunc GL_dst_color GL_one
		tcmod scale -.5 -.5
		tcmod scroll .025 .025
	}	
	{
		map $lightmap
		blendFunc GL_dst_color GL_zero
		rgbgen identity		
	}
}

textures/phantq3ctf1/e8_jumppad02
{	
	surfaceparm nodamage
	q3map_surfacelight 200	
	{
		map textures/phantq3ctf1/e8_jumppad02.tga
		rgbGen identity
	}	
	{
		map $lightmap
		blendfunc gl_dst_color gl_zero
		rgbGen identity
	}	
	{
		animMap 2 textures/phantq3ctf1/phant_jumppad_fx_blue.tga textures/phantq3ctf1/phant_jumppad_fx_blue.tga textures/phantq3ctf1/phant_jumppad_fx_blue.tga textures/phantq3ctf1/phant_jumppad_fx_blue.tga  textures/phantq3ctf1/phant_jumppad_fx_blue.tga textures/phantq3ctf1/phant_jumppad_fx_blue.tga textures/phantq3ctf1/phant_jumppad_fx_blue.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave inverseSawtooth 0 1 0 2
	}	
}

textures/phantq3ctf1/e8_jumppad02_red
{
	surfaceparm nodamage
	q3map_surfacelight 200	
	{
		map textures/phantq3ctf1/e8_jumppad02_red.tga
		rgbGen identity
	}	
	{
		map $lightmap
		blendfunc gl_dst_color gl_zero
		rgbGen identity
	}	
	{
		animMap 2 textures/phantq3ctf1/phant_jumppad_fx_red.tga textures/phantq3ctf1/phant_jumppad_fx_red.tga textures/phantq3ctf1/phant_jumppad_fx_red.tga textures/phantq3ctf1/phant_jumppad_fx_red.tga  textures/phantq3ctf1/phant_jumppad_fx_red.tga textures/phantq3ctf1/phant_jumppad_fx_red.tga textures/phantq3ctf1/phant_jumppad_fx_red.tga
		blendFunc GL_ONE GL_ONE
		rgbGen wave inverseSawtooth 0 1 0 2
	}	
}

textures/phantq3ctf1/e8jumpspawn02
{
	q3map_lightimage textures/phantq3ctf1/e8jumpspawn02_fx.tga
	surfaceparm metalsteps
	q3map_surfacelight 100
	{
		map textures/phantq3ctf1/e8jumpspawn02_fx.tga
		rgbGen identity
		tcMod rotate 760
	}
	{
		map textures/phantq3ctf1/e8jumpspawn02.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc gl_dst_color gl_one_minus_dst_alpha
		rgbGen identity
		tcGen lightmap 
	}
}

textures/phantq3ctf1/e8tinylight
{
	qer_editorimage textures/phantq3ctf1/e8tinylight.tga
	q3map_lightimage textures/phantq3ctf1/e8tinylight_blend.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/e8tinylight.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/e8tinylight_blend.tga
		blendfunc add
	}
}


textures/phantq3ctf1/e8tinylight_decal
{

   qer_editorimage textures/phantq3ctf1/e8tinylight.tga
   surfaceparm nodamage
   q3map_lightimage textures/phantq3ctf1/e8tinylight_blend.tga
   surfaceparm nonsolid
   surfaceparm nomarks
   surfaceparm trans
   polygonoffset
   {
      map textures/phantq3ctf1/e8tinylight.tga
      blendfunc add
      rgbGen Vertex
   }

	{
		map textures/phantq3ctf1/e8tinylight_blend.tga
		blendfunc add
	}
}

textures/phantq3ctf1/evil8_rlight
{
	qer_editorimage textures/phantq3ctf1/e8_rlight.tga
	q3map_lightimage textures/phantq3ctf1/e8_rlight_blend.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/e8_rlight.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/e8_rlight_blend.tga
		blendfunc add
	}
}

textures/phantq3ctf1/e8trimlight2_blue
{
	qer_editorimage textures/phantq3ctf1/e8trimlight2_blue.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/e8trimlight2_blue.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/e8trimlight2_blue_blend.tga
		blendfunc add
		
	}
}

textures/phantq3ctf1/e8trimlight2_red
{
	qer_editorimage textures/phantq3ctf1/e8trimlight2_red.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/e8trimlight2_red.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/e8trimlight2_red_blend.tga
		blendfunc add
		
	}
}

textures/phantq3ctf1/phant_light_blue
{
	qer_editorimage textures/phantq3ctf1/phant_light_blueglow.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/phant_light_base.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/phant_light_blueglow.tga
		blendfunc add
		
	}
}

textures/phantq3ctf1/phant_light_red
{
	qer_editorimage textures/phantq3ctf1/phant_light_redglow.tga
	surfaceparm nomarks
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/phant_light_base.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/phant_light_redglow.tga
		blendfunc add
		
	}
}

textures/phantq3ctf1/phant_techlight_01_blue
{
	qer_editorimage textures/phantq3ctf1/phant_techlight_01_blue.tga
	q3map_lightimage textures/phantq3ctf1/phant_techlight_01_blue.tga
	surfaceparm nonsolid
  	surfaceparm nomarks
  	surfaceparm trans
  	polygonoffset
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/phant_techlight_01_base.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/phant_techlight_01_blue.tga
		blendfunc add
	}
}

textures/phantq3ctf1/phant_techlight_01_red
{
	qer_editorimage textures/phantq3ctf1/phant_techlight_01_red.tga
	q3map_lightimage textures/phantq3ctf1/phant_techlight_01_red.tga
   	surfaceparm nonsolid
   	surfaceparm nomarks
  	 surfaceparm trans
  	 polygonoffset
	q3map_surfacelight 950
	{
		map textures/phantq3ctf1/phant_techlight_01_base.tga
	}
	{
		map $lightmap 
		blendfunc filter
		tcGen lightmap 
	}
	{
		map textures/phantq3ctf1/phant_techlight_01_red.tga
		blendfunc add
	}
}


textures/phantq3ctf1/e6metalfan_blade
{
        surfaceparm trans	
        surfaceparm nomarks	
	cull none
        nopicmip
	{
		clampmap textures/phantq3ctf1/e6metalfan_blade.tga
		tcMod rotate 999
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

//---------------------------------Grates-----------------------------

textures/phantq3ctf1/e8bgrate01
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	cull disable
	{
		map textures/phantq3ctf1/e8bgrate01.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/phantq3ctf1/e8xgirder
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	cull disable
	nopicmip
	{
		map textures/phantq3ctf1/e8xgirder.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/phantq3ctf1/e8xgirder_small
{
	cull disable
	{
		map textures/phantq3ctf1/e8xgirder_small.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

textures/phantq3ctf1/e6metalfan
{
        surfaceparm trans	
        surfaceparm nomarks	
        surfaceparm	metalsteps	
	cull none
        nopicmip
	{
		map textures/phantq3ctf1/e6metalfan.tga
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

textures/phantq3ctf1/e6girdersupport
{
	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans
	cull disable
	nopicmip
	{
		map textures/phantq3ctf1/e6girdersupport.tga
		rgbGen identity
		depthWrite
		alphaFunc GE128
	}
	{
		map $lightmap 
		blendfunc filter
		rgbGen identity
		tcGen lightmap 
		depthFunc equal
	}
}

//-----------------------------Decals--------------------

textures/phantq3ctf1/e8red_dcl
{
   qer_editorimage textures/phantq3ctf1/e8red_dcl.tga
   surfaceparm nodamage
   surfaceparm nolightmap
   surfaceparm nonsolid
   surfaceparm nomarks
   surfaceparm trans
   polygonoffset
   {
      map textures/phantq3ctf1/e8red_dcl.tga
      blendfunc add
      rgbGen Vertex
   }
}

textures/phantq3ctf1/e8blue_dcl
{
   qer_editorimage textures/phantq3ctf1/e8blue_dcl.tga
   surfaceparm nodamage
   surfaceparm nolightmap
   surfaceparm nonsolid
   surfaceparm nomarks
   surfaceparm trans
   polygonoffset
   {
      map textures/phantq3ctf1/e8blue_dcl.tga
      blendfunc add
      rgbGen Vertex
   }
}

//----------------------------Floor Sounds-------------------

textures/phantq3ctf1/e8metal03c_shiney
{
	qer_editorimage textures/phantq3ctf1/e8metal03c.tga
	{
		map textures/effects/tinfx.tga
		rgbGen identity
		tcGen environment 
	}
	{
		map textures/phantq3ctf1/e8metal03c.tga
		blendfunc blend
		rgbGen identity
	}
	{
		map $lightmap 
		blendfunc gl_dst_color gl_one_minus_dst_alpha
		rgbGen identity
		tcGen lightmap 
	}
}

textures/phantq3ctf1/e8clangfloor05
{
	surfaceparm metalsteps
	{
		map $lightmap
		rgbGen identity
		tcGen lightmap
	}
	{
		map textures/phantq3ctf1/e8clangfloor05.tga
		blendfunc filter
		rgbGen identity
	}
}


