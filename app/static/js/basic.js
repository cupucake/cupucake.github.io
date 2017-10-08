$("input:checkbox[name=type]:checked").each(function(){
    yourArray.push($(this).val());
});