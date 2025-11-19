/////////////////////////////////////////////////////////////////
////////	SHADER FILE FOR "INDUSTRIAL ACCIDENT"	/////
/////////////////////////////////////////////////////////////////

textures/crn_master/crn02_banner
{
	qer_editorimage textures/crn_master/crn02_c_ind.tga
	surfaceparm nomarks
	surfaceparm nolightmap

	{
		map textures/crn_master/crn02_c_ind.tga
		rgbGen identity
		tcMod scroll 0.25 0
	}
}

textures/crn_master/crn02_bluesteel
{
	qer_editorimage textures/crn_master/blueshiny.tga

	{
		map textures/crn_master/bluefx.tga
		rgbGen identity
		tcGen environment
		//tcmod scale 1 1
	}
	{
		map textures/crn_master/blueshiny.tga
		blendfunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		rgbGen identity
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/crn_master/crn02_coolantflow
{
	qer_editorimage textures/crn_master/crn02_coolant1.tga
	q3map_lightimage textures/crn_master/crn02_coolant1.tga
	q3map_globaltexture
	qer_trans .5
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	surfaceparm trans
	q3map_surfacelight 1000
	//tessSize 64
	cull disable
	//deformVertexes wave 100 sin 0 1 .5 .8

	{
		map textures/crn_master/crn02_coolant2.tga
		tcMod turb .3 .2 1 .05
		tcMod scale 1.5 .5
		tcMod scroll 0 -4.2
	}
	{
		map textures/crn_master/crn02_coolant1.tga
		blendfunc add
		tcMod turb .3 .7 1 .05
		tcMod scale 1 .5
		tcMod scroll 0 -4
	}
}


textures/crn_master/crn02_flatcool
{
	qer_editorimage textures/crn_master/crn02_coolant1.tga
	q3map_lightimage textures/crn_master/crn02_coolant1.tga
	q3map_globaltexture
	qer_trans .5
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	surfaceparm trans
	q3map_surfacelight 500
	cull disable

	{
		map textures/crn_master/crn02_coolant2.tga
		tcMod turb .3 .2 1 .05
		tcMod scroll .01 .01
	}
	{
		map textures/crn_master/crn02_coolant1.tga
		blendfunc add
		tcMod turb .2 .1 1 .05
		tcMod scale .5 .5
		tcMod scroll .01 .01
	}
	{
		map textures/crn_master/crn02_coolbubbles.tga
		blendfunc filter
		tcMod turb .2 .1 .1 .2
		tcMod scale .05 .05
		tcMod scroll .001 .001
	}
}

textures/crn_master/crn02_flatlava
{
	qer_editorimage textures/liquids/lavahell.tga
	q3map_lightimage textures/liquids/lavahell.tga
	q3map_globaltexture
	qer_trans .5
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	surfaceparm trans
	q3map_surfacelight 400
	cull disable

	{
		map textures/liquids/lavahell.tga
		tcMod turb .3 .2 1 .05
		tcMod scroll .01 .01
	}
	{
		map textures/crn_master/crn_lavahell.tga
		blendfunc add
		tcMod turb .2 .1 1 .05
		tcMod scale .5 .5
		tcMod scroll .01 .01
	}
	{
		map textures/crn_master/lavatop.tga
		blendfunc filter
		//tcMod turb .2 .1 .1 .2
		tcMod scale .25 .25
		tcMod scroll .001 .001
	}
}


textures/crn_master/crn02_lavaflow
{
	qer_editorimage textures/liquids/lavahell.tga
	q3map_lightimage textures/liquids/lavahell.tga
	q3map_globaltexture
	qer_trans .5
	surfaceparm noimpact
	surfaceparm lava
	surfaceparm nolightmap
	surfaceparm trans
	q3map_surfacelight 1000
	//tessSize 64
	cull disable
	//deformVertexes wave 100 sin 0 1 .5 .8

	{
		map textures/liquids/lavahell.tga
		tcMod turb .3 .2 1 .05
		tcMod scale 1.5 .5
		tcMod scroll 0 -3.8
	}
	{
		map textures/crn_master/crn_lavahell.tga
		blendfunc add
		tcMod turb .3 .7 1 .05
		tcMod scale 1 .5
		tcMod scroll 0 -2.8
	}
}

textures/crn_master/crn02_mastersky
{
	qer_editorimage textures/skies/topclouds.tga
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm sky
	q3map_sun 0.9 0.9 1 70 0 90
	q3map_surfacelight 100
	skyparms env/xnight2 4096 -

	{
		map textures/skies/topclouds.tga
		blendfunc add
		tcMod scroll 0 0.02
		tcMod scale 3.5 1
	}
	{
		map textures/skies/topclouds.tga
		blendfunc add
		tcMod scroll 0.005 0.01
		tcMod scale 4 1
	}
}

textures/crn_master/crn02_pitfog
{
	qer_editorimage textures/liquids/kc_fogcloud3.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm fog
	surfaceparm nodrop
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_surfacelight 35
	fogparms ( 0.3 0.4 0.8 ) 400

	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc filter
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc filter
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}


textures/crn_master/crn02_redblinker
{
	q3map_lightimage textures/base_light/proto_lightred.tga
	qer_editorimage textures/base_light/proto_lightred.tga
	surfaceparm nomarks
	q3map_surfacelight 200

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/proto_lightred.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/base_light/proto_lightred.tga
		blendfunc add
		rgbGen wave inversesawtooth .2 .8 0 0.4
	}
}

textures/crn_master/crn02_blueblinker
{
	q3map_lightimage textures/crn_master/proto_lightblue.tga
	qer_editorimage textures/crn_master/proto_lightblue.tga
	surfaceparm nomarks
	q3map_surfacelight 200

	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/crn_master/proto_lightblue.tga
		blendfunc filter
		rgbGen identity
	}
	{
		map textures/crn_master/proto_lightblue.tga
		blendfunc add
		rgbGen wave inversesawtooth .2 .8 0 0.4
	}
}

textures/crn_master/crn02_redfog
{
	qer_editorimage textures/liquids/kc_fogcloud3.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm fog
	surfaceparm nodrop
	surfaceparm nolightmap
	q3map_globaltexture
	fogparms ( 0.8 0.2 0.3 ) 448

	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc filter
		tcmod scale -.05 -.05
		tcmod scroll .01 -.01
		rgbgen identity
	}
	{
		map textures/liquids/kc_fogcloud3.tga
		blendfunc filter
		tcmod scale .05 .05
		tcmod scroll .01 -.01
		rgbgen identity
	}
}

textures/crn_master/crn02_redsteel
{
	qer_editorimage textures/crn_master/redshiny.tga

	{
		map textures/crn_master/redfx.tga
		rgbGen identity
		tcGen environment
		//tcmod scale .25 .25
	}
	{
		map textures/crn_master/redshiny.tga
		blendfunc GL_ONE_MINUS_SRC_ALPHA GL_SRC_ALPHA
		rgbGen identity
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/crn_master/redglass
{
	qer_editorimage textures/crn_master/redfx.tga
	qer_trans 0.5
	surfaceparm trans
	sort 7
	{
		map textures/crn_master/redfx.tga
		blendfunc add
		rgbGen identitylighting
		tcGen environment
	}
	{
		map textures/crn_master/glassmap.tga
		blendfunc add
		rgbGen identitylighting
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/crn_master/blueglass
{
	qer_editorimage textures/crn_master/bluefx.tga
	qer_trans 0.5
	surfaceparm trans
	sort 7
	{
		map textures/crn_master/bluefx.tga
		blendfunc add
		rgbGen identitylighting
		tcGen environment
	}
	{
		map textures/crn_master/glassmap.tga
		blendfunc add
		rgbGen identitylighting
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}


textures/crn_master/crn02_sign
{
	qer_editorimage textures/crn_master/crn02_better.tga
	surfaceparm nodamage
	Surfaceparm nolightmap

	{
		animMap 0.7 textures/crn_master/crn02_better.tga textures/crn_master/crn02_thru.tga textures/crn_master/crn02_tech.tga
		blendfunc add
		rgbGen wave inversesawtooth 0 1 0 0.7
	}
	{
		map textures/base_wall/comp3text.tga
		blendfunc add
		rgbGen identity
		tcmod scroll 3 0.7
	}
	{
		map textures/skies/topclouds.tga
		tcgen environment
		rgbGen identity
		blendfunc add
	}
}

textures/crn_master/patch_beatup
{
	qer_editorimage textures/crn_master/mapp_conc_dark.tga

	{
	map textures/base_wall/patch10_beatup2.tga
	rgbGen identity
	}
	{
	map $lightmap
	blendfunc filter
	rgbgen identity
	}
}

textures/crn_master/smooth_concrete
{
	qer_editorimage textures/crn_master/mapp_conc_dark.tga

	{
	map textures/base_wall/concrete_dark.tga
	rgbGen identity
	}
	{
	map $lightmap
	blendfunc filter
	rgbgen identity
	}
}
textures/crn_master/launchpad_blue
{
	qer_editorimage textures/sfx/launchpad_metalbridge04d.tga
	{
		map $lightmap
		rgbGen identity
	}
	{ 
		map textures/sfx/launchpad_metalbridge04d.tga
		rgbGen identity
		blendfunc filter
	}
	{	
		map textures/crn_master/lpad_dot_blue.tga
		blendfunc add	
		rgbgen wave inversesawtooth 0 1 0 1	
	}
	{ 
		animmap 4 textures/crn_master/lpad_arrow_blue.tga textures/sfx/launchpad_arrow2.tga textures/sfx/launchpad_arrow2.tga textures/sfx/launchpad_arrow2.tga
		blendfunc add
		tcmod scroll 0 2
	}

}

textures/crn_master/launchpad_red
{
	qer_editorimage textures/sfx/launchpad_metalbridge04d.tga
	{
		map $lightmap
		rgbGen identity
	}
	{ 
		map textures/sfx/launchpad_metalbridge04d.tga
		rgbGen identity
		blendfunc filter
	}
	{	
		map textures/crn_master/lpad_dot_red.tga
		blendfunc add	
		rgbgen wave inversesawtooth 0 1 0 1	
	}
	{ 
		animmap 4 textures/crn_master/lpad_arrow_red.tga textures/sfx/launchpad_arrow2.tga textures/sfx/launchpad_arrow2.tga textures/sfx/launchpad_arrow2.tga
		blendfunc add
		tcmod scroll 0 2
	}

}

textures/crn_master/patchlight
{
	qer_editorimage textures/crn_master/patch10light.tga
	q3map_lightimage textures/crn_master/patch10light_blend.tga
	q3map_surfacelight 3000

      {
		map textures/crn_master/patch10light.tga
	      rgbGen identity
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
      {
		map textures/crn_master/patch10light_blend.tga
            blendfunc add
		rgbgen identity
	}
}