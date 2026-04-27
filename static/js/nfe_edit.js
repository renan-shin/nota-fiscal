const prefixo_url_tem_bol = url_tem_bol.split('/').slice(0, 3).join('/');
const prefixo_url_boleto = url_boleto.split('/').slice(0, 3).join('/');
const url_final_tem_bol = prefixo_url_tem_bol + '/' + empresa + '/' + id_nfe;
const url_final_boleto = prefixo_url_boleto + '/' + empresa + '/' + id_nfe;

$('#cpf-dest').mask('000.000.000-00', {reverse: true});
$('#cnpj-dest').mask('00.000.000/0000-00', {reverse: true});
$('#cep-dest').mask('00000-000', {reverse: true});
$('#cnpj-transp').mask('00.000.000/0000-00', {reverse: true});

$('#modalGenerico').on('hidden.bs.modal', function() {
    $('#btnStatus').prop('disabled', false);
    $('#textoModal').attr('class', '');
    $('#textoModal').html('');
});

$('#btnBoleto').on('click', function() {
    $('#pdfFrame').remove()
    $('#modalBoleto .modal-body').append("<iframe id='pdfFrame' frameborder='0' style='width: 100%; height: 80vh;' allowfullscreen></iframe>")
    $('#modalBoletoLabel').html('Pedido ' + pedido + ' NF-e ' + ide_nnf)
    document.getElementById('pdfFrame').src = url_final_boleto;
    //new bootstrap.Modal(document.getElementById('pdfModal')).show();
    $('#modalBoleto').modal('show');
})

tem_boleto()

async function tem_boleto() {
    //var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url_final_tem_bol, {
            method: 'GET',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                //'X-CSRFToken': csrfToken,
            },
            //body: $('form').serialize()
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
    } catch(error) {
        //divRetorno.className = 'alert alert-danger';
        //divRetorno.textContent = '-1 - ' + error;
        $('#textoModal').attr('class', 'text-danger fw-bold');
        $('#textoModal').html('-1 - ' + error);
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro Boleto')
        $('#modalGenerico').modal('show');
    } finally {
        var dados = await response.json();

        $('#modalGenerico .modal-title').html('');

        if(dados.erro === false) {
            //divRetorno.className = 'alert alert-danger';
            if(dados.tem_bol && (status_nfe.includes('Aut') || status_nfe.includes('Carta'))) {
                $('#btnBoleto').prop('disabled', false);
            } else {
                $('#btnBoleto').prop('disabled', true);
            }
        } else {
            $('#modalGenerico .modal-title').html('Erro Boleto')
            $('#textoModal').attr('class', 'text-danger fw-bold');
            $('#textoModal').html(dados.mensagem);
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}