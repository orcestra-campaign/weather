function Meta(meta)
    filepath = string.gsub(quarto.doc.output_file, quarto.project.output_directory, "")
    slide_path = string.format("%s/slides%s", quarto.project.offset, filepath)
    if string.match(slide_path, "/briefings/") then
        meta.slide_link = pandoc.Link("Slide Version", slide_path)
        meta.slide_path = slide_path
    else
        meta.slide_link = ""
    end

    return meta
end
