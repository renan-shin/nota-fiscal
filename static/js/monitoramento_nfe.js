async function retransmitir(elemento) {
    let id = $(elemento).data('id');
    let empresa = $(elemento).data('empresa');
    const prefixo_url = url_retransmitir.split('/').slice(0, 3).join('/');
    var url = prefixo_url + '/' + empresa + '/' + id + '/';

    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
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
        $('#textoModal').attr('class', 'text-danger fw-bold');
        $('#textoModal').html('-1 - ' + error);
        $('#overlay').fadeOut();
    } finally {
        var dados = await response.json();

        $('#modalGenerico .modal-title').html(dados.titulo);

        if(dados.status === 100) {
            $('#textoModal').attr('class', 'text-success fw-bold');
        } else {
            $('#textoModal').attr('class', 'text-danger fw-bold');
        }
        
        $('#textoModal').html(dados.mensagem);
        $('#overlay').fadeOut();
    }

    $('#modalGenerico').modal('show');
}