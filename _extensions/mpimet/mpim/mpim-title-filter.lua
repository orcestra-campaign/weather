return {
    {
      Pandoc = function (doc)
        local meta = doc.meta
        local body = doc.blocks

        meta['multiple-affiliations'] = #meta["by-affiliation"] > 1
        meta['has-departments'] = false
        for _, affiliation in ipairs(meta["by-affiliation"]) do
          if affiliation.department then
            meta['has-departments'] = true
          end
        end

        return pandoc.Pandoc(body, meta)
      end
    }
  }