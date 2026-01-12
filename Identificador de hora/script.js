function exibir(){
    var data = new Date()
    var horario = data.getHours()
    var texto = window.document.getElementById("texto")
    var imagem = window.document.getElementById("img")
    var corpo = window.document.getElementById("corpo")
    texto.innerHTML = `Agora são ${horario} horas`
    if (horario>=0 && horario<12){
        imagem.src = "manha.png"
        window.document.body.style.background = "#fee6bd"}
    
        else if(horario>=12 && horario<18){
        imagem.src = "tarde.png"
        window.document.body.style.background="#c35501"}
    
        else if(horario>=18 && horario<=23){
        imagem.src = "noite.png"
        window.document.body.style.background="#3c515e"}
    }