function resultado(){
    var data = new Date()
    
    var ano = data.getFullYear()
    var ano_nasc = window.document.getElementById("ano_nasc").value
    var resposta = window.document.getElementById("resposta")
    var sexo = window.document.getElementsByName("radsex")
    var img = document.createElement("img")
    img.setAttribute("id", "foto")
    var foto = document.getElementById("foto")
    if(ano_nasc>ano || ano_nasc.length ==0){
        window.alert("[ERRO] Verifique os dados preenchidos")}
        
        else if (sexo[0].checked){
        resposta.style.textAlign = "center"
        if (ano-ano_nasc<18){
        resposta.innerText = `Detectamos: Homem com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_criancas.png")}
        else if(ano-ano_nasc>18 && ano-ano_nasc<60){
        resposta.innerText = `Detectamos: Homem com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_adultos.png")} 
        else{
        resposta.innerText = `Detectamos: Homem com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_idosos.png")}}
        
        else if (sexo[1].checked){
        resposta.style.textAlign = "center"
        if (ano-ano_nasc<18){
        resposta.innerText = `Detectamos: Mulher com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_criancas.png")}
        else if(ano-ano_nasc>18 && ano-ano_nasc<60){
        resposta.innerText = `Detectamos: Mulher com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_adultos.png")} 
        else {
        resposta.innerText = `Detectamos: Mulher com ${ano-ano_nasc} anos`
        img.setAttribute("src", "pronto_idosos.png")}
        }
        resposta.appendChild(img)
    }