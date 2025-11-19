/// Divided Crossings Shader ///
////////////////////////////////////////////////////////////////////////
textures/divided/divided_skybox
{
	qer_editorimage gfx/colors/black.tga

	surfaceparm noimpact
//	surfaceparm nolightmap

	q3map_sunExt 0.8 0.8 1 40 90 90 3 16
	q3map_lightmapFilterRadius 0 16
	q3map_skyLight 55 3

//	q3map_sun	0.8 0.8 1 32 90 90 //red green blue intensity degrees elevation
//	q3map_surfacelight 50
//	q3map_lightsubdivide 256
	
	skyparms env/divided/divided - -
}
////////////////////////////////////////////////////////////////////////
// id flare from colua0 model
textures/divided/id_flare
{
	qer_editorimage textures/divided/id_flare.tga
	deformVertexes autoSprite

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none	
	{
		Map textures/divided/id_flare.tga
		blendFunc GL_ONE GL_ONE
	}	
	
}
////////////////////////////////////////////////////////////////////////
textures/divided/id_flare_tele
{
	qer_editorimage textures/divided/jumpadb2.tga
//	deformVertexes autoSprite

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none	
	{
		clampmap textures/divided/jumpadb2.tga
		blendFunc GL_ONE GL_ONE
		//tcMod stretch Sin 1.0 0.5 0.0 5
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave sin .8 .2 .25 1.0
		tcMod rotate 720
	}
	{
		clampmap textures/divided/jumpadb2.tga
		blendFunc GL_ONE GL_ONE
		tcMod stretch sin 0.8 .8 0 1.0
		tcMod rotate -480
	}	
	
}
////////////////////////////////////////////////////////////////////////
textures/divided/id_flare_redtele
{
	qer_editorimage textures/divided/jumpadn2.tga
//	deformVertexes autoSprite

	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nolightmap
	cull none	
	{
		clampmap textures/divided/jumpadn2.tga
		blendFunc GL_ONE GL_ONE
		//tcMod stretch Sin 1.0 0.5 0.0 5
		tcMod stretch sin 1.2 .8 0 1.5
		rgbGen wave sin .8 .2 .25 1.0
		tcMod rotate 720
	}
	{
		clampmap textures/divided/jumpadn2.tga
		blendFunc GL_ONE GL_ONE
		tcMod stretch sin 0.8 .8 0 1.0
		tcMod rotate -480
	}	
	
}
////////////////////////////////////////////////////////////////////////
textures/divided/bounce_white
{
	qer_editorimage textures/ctf_unified/qer_bounce.tga
	q3map_lightimage textures/divided/bounce_fx_white.tga
	q3map_surfacelight 400
	surfaceparm nodamage
	surfaceparm nomarks
	surfaceparm trans

	{
		map textures/ctf_unified/bounce_base.tga
		rgbGen identity
		alphaFunc GE128
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
		depthFunc equal
	}
	{
		map textures/divided/bounce_glow_white.tga
		blendfunc add
		rgbGen wave sin 0.5 0.5 0 1.5
	}
	{
		clampmap textures/divided/bounce_fx_white.tga
		blendfunc add
		tcMod stretch sin 1.2 0.8 0 1.5
		rgbGen wave square 0.5 0.5 0.25 1.5
	}
	{
		map textures/ctf_unified/bounce_shadow.tga
		blendfunc filter
		rgbGen identity
	}
}
////////////////////////////////////////////////////////////////////////