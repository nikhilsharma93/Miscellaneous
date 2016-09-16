function out=word_match(str1,str2,str3)
    stopwords_cellstring=str3;
    str_cmp1=setdiff(strsplit(str1),stopwords_cellstring);
    str_cmp2=setdiff(strsplit(str2),stopwords_cellstring);
    out=length(intersect(str_cmp1,str_cmp2));
end

