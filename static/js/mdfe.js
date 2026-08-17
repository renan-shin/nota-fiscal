$(document).ready(function() {
    const idsColunas = ['id_mdfe', 'ide_nMDF', 'status', 'btnLimpar'];
    const empresas = document.getElementById('empresas');

    const tabela = new DataTable('#manifestos', {
        ajax: {
            url: '../api/manifestos',
            type: 'GET',
            data: function(d) {
                d.id_mdfe = $('#id_mdfe').val();
                d.ide_nMDF = $('#ide_nMDF').val();
                d.status = $('#status').val();
            }
        },
        colReorder: true,
        responsive: true,
        processing: false,
        serverSide: true,
        scrollY: 335,
        scrollX: true,
        searching: false,
        orderMulti: true,
        pageLength: 10,
        order: [[4, 'desc']],
        rowId: 'id_mdfe',
        columns: [
            {'data': 'id_mdfe'},
            {'data': 'ide_nMDF'},
            {'data': 'status'},
            {'data': 'ide_serie'},
            {'data': 'data_criacao'},
            {'data': 'UFIni'},
            {'data': 'UFFim'},
        ],
        columnDefs: [
            {width: '10%', targets: 0, className: 'dt-center'},
            {width: '10%', targets: 1, className: 'dt-center'},
            {width: '20%', targets: 2},
            {width: '7%', targets: 3, className: 'dt-center'},
            {width: '15%', targets: 4, className: 'dt-center'},
            {width: '10%', targets: 5},
            {width: '10%', targets: 6}
        ],
        language: {
            emptyTable: "Nenhum registro encontrado",
            info: 'Mostrando de _START_ até _END_ de _TOTAL_ registros',
            infoEmpty: 'Mostrando 0 até 0 de 0 registros',
            infoFiltered: '(Filtrados de _MAX_ registros)',
            infoThousands: '.',
            loadingRecords: 'Carregando...',
            processing: 'Processando...',
            lengthMenu: 'Exibir _MENU_ resultados por página',
            zeroRecords: 'Nenhum registro encontrado',
            search: "Pesquisar",
                paginate: {
                    next: "Próximo",
                    previous: "Anterior",
                    first: "Primeiro",
                    last: "Último"
                },
        },
        initComplete: function () {
            this.api()
                .on('preXhr', function() {
                    $('#overlay').fadeIn();
                })
                .on('xhr', function() {
                    $('#overlay').fadeOut();
                })
                .columns([0,1,2,3])
                .every(function (index) {
                    let column = this;
                    let title = column.footer().textContent;
                    const idColuna = idsColunas[index];
                    
                    if(title === 'ID' || title === 'MDF-e') {
                        // Create input element
                        let input = document.createElement('input');
                        input.className = 'form-control form-control-sm';
                        input.placeholder = title;
                        input.id = idColuna;
                        input.name = idColuna;
                        input.type = 'number';
                        column.footer().replaceChildren(input);

                        // Event listener for user input
                        input.addEventListener('keyup', (e) => {
                            if (e.key === 'Enter') {
                                atualizaDataTable(empresas.value);
                                column.search(input.value).draw();
                            }
                        });
                    } else if(title === 'Serie') {
                        let botao = document.createElement('button');
                        botao.className = 'btn btn-primary btn-sm';
                        botao.textContent = 'Limpar';
                        botao.id = idColuna;
                        botao.type = 'button';

                        botao.addEventListener('click', () => {
                            limpaFiltros();
                            atualizaDataTable(empresas.value);
                        })

                        column.footer().replaceChildren(botao);
                    } else {
                        let select = document.createElement('select');
                        select.className = 'form-select form-select-sm';
                        select.id = idColuna;
                        select.name = idColuna;
                        column.footer().replaceChildren(select);

                        let emptyOption = document.createElement('option');
                        emptyOption.setAttribute('selected', true);
                        emptyOption.setAttribute('value', '')
                        emptyOption.textContent = 'Status'
                        select.appendChild(emptyOption);
                        
                        // Event listener for user input
                        select.addEventListener('change', () => {
                            if (column.search() !== this.value) {
                                column.search(select.value).draw();
                            }
                        });
                    }
                });
        }
    });

    tabela.on('click', 'tbody tr', (e) => {
        let classList = e.currentTarget.classList;

        tabela.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
        classList.add('selected');
    })

    $('#btnStatus').on('click', function() {
        if(!empresas.value) {
            alert('Selecione uma empresa!');
            return;
        }

        consulta_status();
    });

    empresas.addEventListener('change', function() {
        limpaFiltros();
        atualizaDataTable(this.value);
    });

    function limpaFiltros() {
        document.getElementById('id_mdfe').value = '';
        document.getElementById('ide_nMDF').value = '';
        document.getElementById('status').value = '';
    }

    function atualizaDataTable(cod_empresa) {
        tabela.ajax.url('../api/manifestos/' + cod_empresa).load();

        fetch('../api/status-disponiveis/m/' + cod_empresa)
        .then(res => {return res.json();})
        .then(dados => {
            var lista_status = document.getElementById('status')
            while(lista_status.firstChild)
                lista_status.removeChild(lista_status.firstChild);

            let emptyOption = document.createElement('option');
            emptyOption.setAttribute('selected', true);
            emptyOption.setAttribute('value', '');
            emptyOption.textContent = 'Status';
            lista_status.appendChild(emptyOption);

            dados.status_disponiveis.forEach(element => {
                let opcao = document.createElement('option');
                opcao.setAttribute('value', element.status);
                opcao.textContent = element.status;
                lista_status.appendChild(opcao);
            })
        })
    }

    $('#manifestos tbody').on('dblclick', 'tr', function() {
        const prefixo_url = url.split('/').slice(0, 2).join('/');
        let id_nfe = tabela.row(this).id();
        let empresa_filial = empresas.value;

        window.open(prefixo_url + '/' + empresa_filial + '/' + id_nfe + '/edit/', '_blank');
    })

    $('#btnNovo').on('click', function() {
        if(!empresas.value) {
            alert('Selecione uma empresa!');
            return false;
        }

        $('#modalNovoMDFe').modal('show');
    })

    $('#btnCriar').on('click', function() {
        $('#modalNovoMDFe').modal('hide');
        criar_manifesto();
    })

    async function criar_manifesto() {
        var empresa = empresas.value;
        var url = '../api/criar-manifesto/' + empresa;

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
            $('#overlay').fadeOut();
            alert('-1 - ' + error);
        } finally {
            var dados = await response.json();

            if(!dados.erro) {
                $('#textoModalNovoMDFe').attr('class', 'text-success fw-bold');
                atualizaDataTable(empresas.value);
            }

            $('#overlay').fadeOut();
            alert(dados.mensagem);
        }
    }

    async function consulta_status() {
        //var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        var empresa = empresas.value;
        var url = '../api/consulta-status/' + empresa + '/m';

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
            //divRetorno.className = 'alert alert-danger';
            //divRetorno.textContent = '-1 - ' + error;
            $('#textoModal').attr('class', 'text-danger fw-bold');
            $('#textoModal').html('-1 - ' + error);
            $('#overlay').fadeOut();
        } finally {
            var dados = await response.json();

            $('#modalGenerico .modal-title').html(dados.titulo);

            if(dados.status !== 107) {
                //divRetorno.className = 'alert alert-danger';
                $('#textoModal').attr('class', 'text-danger fw-bold');
            } else {
                $('#textoModal').attr('class', 'text-success fw-bold');
            }

            $('#textoModal').html(dados.mensagem);
            $('#overlay').fadeOut();
        }

        $('#modalGenerico').modal('show');
    }
})

$('#modalGenerico').on('hide.bs.modal', function() {
    if (document.activeElement) {
        document.activeElement.blur();
    }
})

$('#modalNovoMDFe').on('hide.bs.modal', function() {
    if (document.activeElement) {
        document.activeElement.blur();
    }
})