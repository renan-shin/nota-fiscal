const prefixo_url_boleto = url_boleto.split('/').slice(0, 3).join('/');
const url_final_boleto = prefixo_url_boleto + '/' + empresa + '/' + id_nfe;
const prefixo_url_danfe = url_danfe.split('/').slice(0, 3).join('/');
const url_final_danfe = prefixo_url_danfe + '/' + empresa + '/' + id_nfe + '/1/';
const prefixo_url_danfe_cce = url_danfe_cce.split('/').slice(0, 3).join('/');
const url_final_danfe_cce = prefixo_url_danfe_cce + '/' + empresa + '/' + id_nfe + '/1/';
const prefixo_url_cupom = url_cupom.split('/').slice(0, 3).join('/');
const url_final_cupom = prefixo_url_cupom + '/' + empresa + '/' + id_nfe;
let recarregar_pagina = false;

$('#cpf-dest').mask('000.000.000-00', {reverse: true});
$('#cnpj-dest').mask('00.000.000/0000-00', {reverse: true});
$('#cep-dest').mask('00000-000', {reverse: true});
$('#cep-entrega').mask('00000-000', {reverse: true});
$('#cnpj-transp').mask('00.000.000/0000-00', {reverse: true});

$('#modalGenerico').on('hidden.bs.modal', function() {
    $('#modalGenerico .modal-body').html('');
    $('#modalGenericoLabel').html('');

    if(recarregar_pagina) {
        location.reload();
    }

    recarregar_pagina = false;
});

$('#btnBoleto').on('click', function() {
    $('#dialogModal').attr('class', 'modal-dialog modal-fullscreen');
    $('#pdfFrame').remove()
    $('#modalGenerico .modal-body').append("<iframe id='pdfFrame' frameborder='0' style='width: 100%; height: 80vh;' allowfullscreen></iframe>")
    $('#modalGenericoLabel').html('Pedido ' + pedido + ' NF-e ' + ide_nnf)
    document.getElementById('pdfFrame').src = url_final_boleto;
    //new bootstrap.Modal(document.getElementById('pdfModal')).show();
    $('#modalGenerico').modal('show');
})

$('#btnDanfe').on('click', function() {
    $('#dialogModal').attr('class', 'modal-dialog modal-fullscreen');
    $('#pdfFrame').remove()
    $('#modalGenerico .modal-body').append("<iframe id='pdfFrame' frameborder='0' style='width: 100%; height: 80vh;' allowfullscreen></iframe>")
    $('#modalGenericoLabel').html('Pedido ' + pedido + ' NF-e ' + ide_nnf)
    document.getElementById('pdfFrame').src = url_final_danfe;
    //new bootstrap.Modal(document.getElementById('pdfModal')).show();
    $('#modalGenerico').modal('show');
})

$('#btnDanfeCCe').on('click', function() {
    $('#dialogModal').attr('class', 'modal-dialog modal-fullscreen');
    $('#pdfFrame').remove()
    $('#modalGenerico .modal-body').append("<iframe id='pdfFrame' frameborder='0' style='width: 100%; height: 80vh;' allowfullscreen></iframe>")
    $('#modalGenericoLabel').html('Pedido ' + pedido + ' NF-e ' + ide_nnf)
    document.getElementById('pdfFrame').src = url_final_danfe_cce;
    //new bootstrap.Modal(document.getElementById('pdfModal')).show();
    $('#modalGenerico').modal('show');
})

$('#btnCupom').on('click', function() {
    $('#dialogModal').attr('class', 'modal-dialog modal-fullscreen');
    $('#pdfFrame').remove()
    $('#modalGenerico .modal-body').append("<iframe id='pdfFrame' frameborder='0' style='width: 100%; height: 80vh;' allowfullscreen></iframe>")
    $('#modalGenericoLabel').html('Pedido ' + pedido + ' NF-e ' + ide_nnf)
    document.getElementById('pdfFrame').src = url_final_cupom;
    //new bootstrap.Modal(document.getElementById('pdfModal')).show();
    $('#modalGenerico').modal('show');
})

$('#btnXML').on('click', function() {
    abrirXML();
})

$('#formasPagto').on('click', function() {
    calcularFormasPagto()
})

$('#calculoTotais').on('click', function() {
    calcularTotaisNFe()
})

$('#btnAcertaNFe').on('click', function() {
    acertaNFe();
})

async function acertaNFe() {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url_acerta_nfe, {
            method: 'POST',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                //'X-CSRFToken': csrfToken,
            },
            body: "empresa_filial=" + empresa + "&id_nfe=" + id_nfe
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
    } catch(error) {
        $('#dialogModal').attr('class', 'modal-dialog')
        $('#modalGenerico .modal-body').append("<p class='text-danger'>" + error + "</p>");
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro Acerta NF-e')
        $('#modalGenerico').modal('show');
    } finally {
        var dados = await response.json();
        $('#modalGenerico .modal-title').html('');

        if(dados.erro === false) {
            $('#status-nfe').val(dados.nfe.status_sefaz);
            $('#protocolo').val(dados.nfe.nProt);
            $('#protocolo-evento').val(dados.nfe.nProt);
            $('#digito-validador').val(dados.nfe.digVal);
            $('#data-horareceb').val(dados.nfe.dhRecbto);
            $('#tipo-evento').val(dados.nfe.tpEvento);

            $('#dialogModal').attr('class', 'modal-dialog')
            $('#modalGenerico .modal-body').append("<p class='text-success'>" + dados.mensagem + "</p>");
            $('#modalGenerico .modal-title').html('Acerta NF-e')
            $('#modalGenerico').modal('show');
            recarregar_pagina = true;
        } else {
            $('#dialogModal').attr('class', 'modal-dialog')
            $('#modalGenerico .modal-body').append("<p class='text-danger'>" + dados.mensagem + "</p>");
            $('#modalGenerico .modal-title').html('Erro Acerta NF-e')
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}

async function abrirXML() {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url_abrir_xml, {
            method: 'POST',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                //'X-CSRFToken': csrfToken,
            },
            body: "empresa_filial=" + empresa + "&id_nfe=" + id_nfe
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
    } catch(error) {
        $('#dialogModal').attr('class', 'modal-dialog')
        $('#modalGenerico .modal-body').append("<p class='text-danger'>" + error + "</p>");
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro Abrir XML')
        $('#modalGenerico').modal('show');
    } finally {
        const contentType = response.headers.get('content-type');

        if(contentType === 'application/xml') {
            // 1. Converte a resposta em um Blob (Binary Large Object)
            const blob = await response.blob();
            
            // 2. Tenta pegar o nome do arquivo enviado pelo Django no cabeçalho
            // Se não encontrar, define um nome padrão
            const disposition = response.headers.get('Content-Disposition');
            let filename = ide_nnf + "-procNFe.xml";
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1].replaceAll('"', '');
            }

            // 3. Cria uma URL temporária para o Blob
            const urlBlob = window.URL.createObjectURL(blob);
            
            // 4. Cria um link invisível e simula o clique
            const a = document.createElement('a');
            a.href = urlBlob;
            a.download = filename; // Aqui entra o nome da sua variável
            document.body.appendChild(a);
            a.click();
            
            // 5. Limpa a memória
            window.URL.revokeObjectURL(urlBlob);
            document.body.removeChild(a);
        } else {
             var dados = await response.json();

            $('#dialogModal').attr('class', 'modal-dialog')
            $('#modalGenerico .modal-body').append("<p class='text-danger'>" + dados.mensagem + "</p>");
            $('#modalGenerico .modal-title').html('Erro Abrir XML')
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}

async function calcularFormasPagto() {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url_formas_pagto, {
            method: 'POST',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                //'X-CSRFToken': csrfToken,
            },
            body: "empresa_filial=" + empresa + "&id_nfe=" + id_nfe
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
        
    } catch(error) {
        $('#dialogModal').attr('class', 'modal-dialog')
        $('#modalGenerico .modal-body').append("<p class='text-danger'>" + error + "</p>");
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro Formas Pagto')
        $('#modalGenerico').modal('show');
    } finally {
        var dados = await response.json();
        $('#modalGenerico .modal-title').html('');

        if(dados.erro === false) {
            //divRetorno.className = 'alert alert-danger';
            $('#table-formaspagto tbody').html('');

            dados.formas_pagto.forEach(fp => {
                let nFat = dados.nfe.cobr_nFat === null ? '' : dados.nfe.cobr_nFat;
                let indPag = fp.pagamento_indPag_Opc === 0 ? 'Pagamento à vista' : 'Pagamento à prazo';
                let valor = fp.pagamento_vPag.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })

                $('#table-formaspagto tbody').append("<tr><td>" + fp.pagamento_nForma + "</td><td>" + indPag + "</td><td>" + 
                    fp.pagamento_tPag__Descricao + "</td><td>" + valor + "</td></tr>");
            });

            let cobr_vliq = 0;
            let cobr_vorig = 0;
            let cobr_nfat = '';

            cobr_vliq = cobr_vliq.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })

            cobr_vorig = cobr_vorig.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })

            if(dados.nfe.cobr_vLiq) {
                cobr_vliq = dados.nfe.cobr_vLiq.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })
            }

            if(dados.nfe.cobr_vOrig) {
                cobr_vorig = dados.nfe.cobr_vOrig.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })
            }

            if(dados.nfe.cobr_nFat) {
                cobr_nfat = dados.nfe.cobr_nFat;
            }

            $('#cobr-nfat').val(cobr_nfat);
            $('#cobr-vliq').val(cobr_vliq);
            $('#cobr-vorig').val(cobr_vorig);
        } else {
            $('#dialogModal').attr('class', 'modal-dialog')
            $('#modalGenerico .modal-title').html('Erro Formas Pagto')
            $('#modalGenerico .modal-body').append("<p class='text-danger fw-bold'>" + dados.mensagem + "</p>");
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}

async function calcularTotaisNFe() {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url_calculo_totais, {
            method: 'POST',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                //'X-CSRFToken': csrfToken,
            },
            body: "empresa_filial=" + empresa + "&id_nfe=" + id_nfe
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
    } catch(error) {
        $('#dialogModal').attr('class', 'modal-dialog')
        $('#modalGenerico .modal-body').append("<p class='text-danger'>" + error + "</p>");
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro Cálculo Totais')
        $('#modalGenerico').modal('show');
    } finally {
        var dados = await response.json();
        $('#modalGenerico .modal-title').html('');

        if(dados.erro === false) {
            //divRetorno.className = 'alert alert-danger';
            $('#table-formaspagto tbody').html('');

            $('#icms-bc').val((dados.nfe.TotalICMS_vBC ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-ipi').val((dados.nfe.TotalICMS_vIPI ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#outras-despesas').val((dados.nfe.TotalICMS_vOutro ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-trib').val((dados.nfe.TotalICMS_vTotTrib ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#ibs-cbs-bc').val((dados.nfe.IBSCBSTot_vBCIBSCBS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-nf').val((dados.nfe.TotalICMS_vNF ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-icms').val((dados.nfe.TotalICMS_vICMS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-pis').val((dados.nfe.TotalICMS_vPIS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-frete').val((dados.nfe.TotalICMS_vFrete ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#icms-inter-ufdest').val((dados.nfe.TotalICMS_vICMSUFDest_Opc ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-ibsuf').val((dados.nfe.IBSTot_vIBS_UF ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#nf-ibs-cbs').val((dados.nfe.totalRTC_vNFTot ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#icms-st-bc').val((dados.nfe.TotalICMS_vBCST ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-cofins').val((dados.nfe.TotalICMS_vCOFINS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-seguro').val((dados.nfe.TotalICMS_vSeg ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#icms-inter-ufremet').val((dados.nfe.TotalICMS_vICMSUFRemet_Opc ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-ibs').val((dados.nfe.IBSTot_vIBS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-icms-st').val((dados.nfe.TotalICMS_vST ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-produtos').val((dados.nfe.TotalICMS_vProd ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-desconto').val((dados.nfe.TotalICMS_vDesc ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#icms-fcp-ufdest').val((dados.nfe.TotalICMS_vFCPUFDest_Opc ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));

            $('#valor-cbs').val((dados.nfe.CBSTot_vCBS ?? 0).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));
        } else {
            $('#dialogModal').attr('class', 'modal-dialog')
            $('#modalGenerico .modal-title').html('Erro Cálculo Totais')
            $('#modalGenerico .modal-body').append("<p class='text-danger fw-bold'>" + dados.mensagem + "</p>");
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}

async function acaoNFe(url, token, acao) {
    $('#overlay').fadeIn();

    try {
        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Token ' + token,
                //'X-CSRFToken': csrfToken,
            },
            body: "empresa=" + empresa + "&id=" + id_nfe
        });

        if(!response.ok) {
            throw new Error('Erro na requisição!');
        }
        
    } catch(error) {
        $('#dialogModal').attr('class', 'modal-dialog')
        $('#modalGenerico .modal-body').append("<p class='text-danger'>" + error + "</p>");
        $('#overlay').fadeOut();
        $('#modalGenerico .modal-title').html('Erro ' + acao)
        $('#modalGenerico').modal('show');
    } finally {
        var dados = await response.json();
        $('#modalGenerico .modal-title').html('');
        $('#dialogModal').attr('class', 'modal-dialog')

        if(dados.erro === false) {
            $('#modalGenerico .modal-title').html('Retorno')
            $('#modalGenerico .modal-body').append("<p class='text-success fw-bold'>" + dados.mensagem + "</p>");
            $('#modalGenerico').modal('show');
            recarregar_pagina = true;
        } else {
            $('#modalGenerico .modal-title').html('Erro ' + acao)
            $('#modalGenerico .modal-body').append("<p class='text-danger fw-bold'>" + dados.mensagem + "</p>");
            $('#modalGenerico').modal('show');
        }

        $('#overlay').fadeOut();
    }
}

$('#btnTransmitir').on('click', function() {
    const url = $(this).data('url');
    const tokenElement = document.getElementById('token-data');
    const token = JSON.parse(tokenElement.textContent);
    acaoNFe(url, token, "Emissão");
})

$('#btnCCe').on('click', function() {
    const url = $(this).data('url');
    const tokenElement = document.getElementById('token-data');
    const token = JSON.parse(tokenElement.textContent);
    acaoNFe(url, token, 'CC-e');
})

$('#btnCancelar').on('click', function() {
    const url = $(this).data('url');
    const tokenElement = document.getElementById('token-data');
    const token = JSON.parse(tokenElement.textContent);
    acaoNFe(url, token, 'Cancelamento');
})