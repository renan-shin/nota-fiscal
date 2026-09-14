$('#chaves_nfe').on('click', '.btn-excluir', function() {
    var $botao = $(this);
    var url = $botao.data('url');
    var id = $botao.data('id');

    if(confirm('Tem certeza que deseja excluir esta NF-e?')) {
        excluir_nfe_manifesto(url, id)
    }
})

$('#ufs').on('click', '.btn-excluir', function() {
    var $botao = $(this);
    var url = $botao.data('url');
    var id = $botao.data('id');

    if(confirm('Tem certeza que deseja excluir esta UF do percurso?')) {
        excluir_percurso_manifesto(url, id)
    }
})

$('#btnPesquisar').on('click', function() {
    var url = $(this).data('url');

    inserir_nfe_manifesto(url);
})

$('#btnAdicionar').on('click', function() {
    var url = $(this).data('url');

    inserir_percurso_manifesto(url);
})

async function inserir_percurso_manifesto(url) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    //'X-CSRFToken': csrfToken,
                },
                body: "empresa_filial=" + empresa + "&id_mdfe=" + id_mdfe + "&uf=" + $('#select-uf').val()
            });

            if(!response.ok) {
                throw new Error('Erro na requisição!');
            }
    } catch(error) {
        //divRetorno.className = 'alert alert-danger';
        //divRetorno.textContent = '-1 - ' + error;
        alert(error);
        $('#overlay').fadeOut();
    } finally {
        var dados = await response.json();

        if(dados.erro) {
            alert(dados.mensagem);
        } else {
            $('#select-uf').val('');

            var novo_registro = 
            "<tr id='uf-" + dados.registro.id + "'>" +
            "<td><button type='button' class='btn btn-sm btn-danger btn-excluir' data-id='" + dados.registro.id + "' data-url='/api/excluir-percurso-manifesto/" + dados.registro.id + "/'>X</button>" +
            "</td><td>" + dados.registro.uf + "</td><td>" + dados.registro.ordem + "</td></tr>"

            $('#ufs tbody').append(novo_registro);
        }

        $('#overlay').fadeOut();
    }
}

async function excluir_percurso_manifesto(url, id) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    //'X-CSRFToken': csrfToken,
                },
                body: "empresa_filial=" + empresa + "&id_mdfe=" + id_mdfe
            });

            if(!response.ok) {
                throw new Error('Erro na requisição!');
            }
    } catch(error) {
        //divRetorno.className = 'alert alert-danger';
        //divRetorno.textContent = '-1 - ' + error;
        alert(error);
        $('#overlay').fadeOut();
    } finally {
        var dados = await response.json();

        if(dados.erro) {
            alert(dados.mensagem);
        } else {
            $(`#uf-${id}`).fadeOut(300, function() {
                $(this).remove();
            })
        }

        $('#overlay').fadeOut();
    }
}

async function inserir_nfe_manifesto(url) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    //'X-CSRFToken': csrfToken,
                },
                body: "empresa_filial=" + empresa + "&id_mdfe=" + id_mdfe + "&pedido=" + $('#pedido').val()
            });

            if(!response.ok) {
                throw new Error('Erro na requisição!');
            }
    } catch(error) {
        //divRetorno.className = 'alert alert-danger';
        //divRetorno.textContent = '-1 - ' + error;
        alert(error);
        $('#overlay').fadeOut();
    } finally {
        var dados = await response.json();

        if(dados.erro) {
            alert(dados.mensagem);
        } else {
            $('#pedido').val('');

            let valor_nfe = 0;
            let peso_nfe = 0;
            let valor_total_nfe = 0
            let peso_total_nfe = 0

            valor_nfe = valor_nfe.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })

            peso_nfe = peso_nfe.toLocaleString('pt-BR', {
                minimumFractionDigits: 4,
                maximumFractionDigits: 4
            })

            valor_total_nfe = valor_total_nfe.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })

            peso_total_nfe = peso_total_nfe.toLocaleString('pt-BR', {
                minimumFractionDigits: 4,
                maximumFractionDigits: 4
            })

            if(dados.registro.ValorNFe) {
                valor_nfe = dados.registro.ValorNFe.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })
            }

            if(dados.registro.PesoNFe) {
                peso_nfe = dados.registro.PesoNFe.toLocaleString('pt-BR', {
                    minimumFractionDigits: 4,
                    maximumFractionDigits: 4
                })
            }

            if(dados.valor_total) {
                valor_total_nfe = dados.valor_total.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })
            }

            if(dados.peso_total) {
                peso_total_nfe = dados.peso_total.toLocaleString('pt-BR', {
                    minimumFractionDigits: 4,
                    maximumFractionDigits: 4
                })
            }

            const novo_registro = 
            "<tr id='chave-" + dados.registro.id + "'>" +
            "<td><button type='button' class='btn btn-sm btn-danger btn-excluir' data-id='" + dados.registro.id + "' data-url='/api/excluir-nfe-manifesto/" + dados.registro.id + "/'>X</button>" +
            "</td><td>" + dados.registro.chave_nfe + "</td>" +
            "<td>" + dados.registro.cMunCarrega + "</td>" +
            "<td>" + dados.registro.xMunCarrega + "</td>" +
            "<td>" + dados.registro.cMunDescarrega + "</td>" +
            "<td>" + dados.registro.xMunDescarrega + "</td>" +
            "<td>" + valor_nfe + "</td>" +
            "<td>" + peso_nfe + "</td></tr>"

            $('#total-valor').val(valor_total_nfe)
            $('#total-peso').val(peso_total_nfe)
            $('#info-compl').val(dados.info_compl)

            $('#chaves_nfe tbody').append(novo_registro);
        }

        $('#overlay').fadeOut();
    }
}

async function excluir_nfe_manifesto(url, id) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    //'X-CSRFToken': csrfToken,
                },
                body: "empresa_filial=" + empresa + "&id_mdfe=" + id_mdfe
            });

            if(!response.ok) {
                throw new Error('Erro na requisição!');
            }
    } catch(error) {
        //divRetorno.className = 'alert alert-danger';
        //divRetorno.textContent = '-1 - ' + error;
        alert(error);
        $('#overlay').fadeOut();
    } finally {
        var dados = await response.json();

        let valor_total_nfe = 0
        let peso_total_nfe = 0

        valor_total_nfe = valor_total_nfe.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })

        peso_total_nfe = peso_total_nfe.toLocaleString('pt-BR', {
            minimumFractionDigits: 4,
            maximumFractionDigits: 4
        })

        if(dados.valor_total) {
            valor_total_nfe = dados.valor_total.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })
        }

        if(dados.peso_total) {
            peso_total_nfe = dados.peso_total.toLocaleString('pt-BR', {
                minimumFractionDigits: 4,
                maximumFractionDigits: 4
            })
        }

        if(dados.erro) {
            alert(dados.mensagem);
        } else {
            $(`#chave-${id}`).fadeOut(300, function() {
                $(this).remove();
                $('#total-valor').val(valor_total_nfe);
                $('#total-peso').val(peso_total_nfe);
                $('#info-compl').val(dados.info_compl);
            })
        }

        $('#overlay').fadeOut();
    }
}

async function acao_manifesto(url) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    //'X-CSRFToken': csrfToken,
                },
                body: "empresa_filial=" + empresa + "&id_mdfe=" + id_mdfe
            });

            if(!response.ok) {
                throw new Error('Erro na requisição!');
            }
    } catch(error) {
        alert(error);
        location.reload();
    } finally {
        var dados = await response.json();
        alert(dados.mensagem);
        location.reload();
    }
}

$('#transmitir').on('click', function() {
    $('#modalGenericoLabel').attr('class', 'modal-title text-success');
    $('#modalGenericoLabel').text('Transmitir Manifesto');
    $('#modal-body').html('<label class="fw-bold">Deseja transmitir o manifesto?</label>');
    $('#acao').attr('class', 'btn btn-success');
    $('#acao').attr('data-url', url_transmitir);
    $('#acao').text('Transmitir');
    $('#modalGenerico').modal('show');
})

$('#encerrar').on('click', function() {
    $('#modalGenericoLabel').attr('class', 'modal-title text-warning');
    $('#modalGenericoLabel').text('Encerrar Manifesto');
    $('#modal-body').html('<label class="fw-bold">Deseja encerrar o manifesto?</label>');
    $('#acao').attr('class', 'btn btn-warning');
    $('#acao').attr('data-url', url_encerrar);
    $('#acao').text('Encerrar');
    $('#modalGenerico').modal('show');
})

$('#cancelar').on('click', function() {
    $('#modalGenericoLabel').attr('class', 'modal-title text-danger');
    $('#modalGenericoLabel').text('Cancelar Manifesto');
    $('#modal-body').html('<label class="fw-bold">Deseja cancelar o manifesto?</label>');
    $('#acao').attr('class', 'btn btn-danger');
    $('#acao').attr('data-url', url_cancelar);
    $('#acao').text('Cancelar');
    $('#modalGenerico').modal('show');
})

$('#acao').on('click', function() {
    const url = $(this).attr('data-url');
    
    acao_manifesto(url);
})