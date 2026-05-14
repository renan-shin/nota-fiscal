$(function() {
    var segundos = 10;
    var contagem_regressiva = segundos;

    var refreshInterval = setInterval(function() {
        contagemRegressiva();
    }, 1000);

    function contagemRegressiva() {
        if(contagem_regressiva == 0) {
            contagem_regressiva = segundos;
            location.reload();
        }

        if(contagem_regressiva < 10)
            document.getElementById("refresh_time").textContent = 'Atualizando em 0' + contagem_regressiva + 'seg...';
        else
            document.getElementById("refresh_time").textContent = 'Atualizando em ' + contagem_regressiva + 'seg...';

        contagem_regressiva = contagem_regressiva - 1;
    }
})