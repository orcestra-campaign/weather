quarto.log.output('dependency extension')
if quarto.doc.is_format("revealjs") then
    quarto.doc.add_html_dependency({
        name="mpim_slide_style",
        version="1",
        stylesheets={"slide_background.css"}
    })
end

if quarto.doc.is_format("html") then
    quarto.doc.add_html_dependency({
        name="mpim_poster_style",
        version="1",
        stylesheets={"poster_background.css"}
    })
end

quarto.doc.add_html_dependency({
    name="mpim_font",
    version="1",
    stylesheets={"fonts/fonts.css"}
})
