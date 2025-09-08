const idsColunas = ['pedido', 'nfe', 'status', 'btnLimpar'];
const empresas = document.getElementById('empresas');

const tabela = new DataTable('#notas-fiscais', {
    ajax: {
        url: '../api/notas-fiscais',
        type: 'GET',
        data: function(d) {
            d.pedido = $('#pedido').val();
            d.nfe = $('#nfe').val();
            d.status = $('#status').val();
        }
    },
    colReorder: true,
    responsive: true,
    processing: true,
    serverSide: true,
    scrollY: 335,
    scrollX: true,
    searching: false,
    orderMulti: true,
    pageLength: 10,
    order: [[4, 'desc']],
    columns: [
        {'data': 'Pedido'},
        {'data': 'ide_nNF'},
        {'data': 'status_sefaz'},
        {'data': 'ide_serie'},
        {'data': 'dtp'},
        {'data': 'dest_xNome'},
    ],
    columnDefs: [
        {width: '10%', targets: 0, className: 'dt-center'},
        {width: '10%', targets: 1, className: 'dt-center'},
        {width: '20%', targets: 2},
        {width: '7%', targets: 3, className: 'dt-center'},
        {width: '15%', targets: 4, className: 'dt-center'},
        {width: '38%', targets: 5}
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
            .columns([0,1,2,3])
            .every(function (index) {
                let column = this;
                let title = column.footer().textContent;
                const idColuna = idsColunas[index];
                
                if(title === 'Pedido' || title === 'NFe') {
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
                            if(title === 'Pedido') {
                                fetch('../api/consulta-empresa/' + Number(input.value))
                                .then(res => {return res.json();})
                                .then(dados => {
                                    empresas.value = dados.empresa_filial;
                                    atualizaDataTable(dados.empresa_filial);
                                });
                            }
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

tabela.on('dblclick', 'tbody tr', (e) => {
    let dados = tabela.row(e.currentTarget).data();
    alert(dados.Pedido);
})

empresas.addEventListener('change', function() {
    limpaFiltros();
    atualizaDataTable(this.value);
});

function limpaFiltros() {
    document.getElementById('pedido').value = '';
    document.getElementById('nfe').value = '';
    document.getElementById('status').value = '';
}

function atualizaDataTable(cod_empresa) {
    tabela.ajax.url('../api/notas-fiscais/' + cod_empresa).load();

    fetch('../api/status-disponiveis/' + cod_empresa)
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
            opcao.setAttribute('value', element.status_sefaz);
            opcao.textContent = element.status_sefaz;
            lista_status.appendChild(opcao);
        })
    })
}

async function consulta_status() {
    //var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var empresa = empresas.value;
    var url = 'api/consulta-status/' + empresa;

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

        $('#modalStatus .modal-title').html(dados.titulo);

        if(dados.status !== 107) {
            //divRetorno.className = 'alert alert-danger';
            $('#textoModal').attr('class', 'text-danger fw-bold');
        } else {
            $('#textoModal').attr('class', 'text-success fw-bold');
        }

        $('#textoModal').html(dados.mensagem);
        $('#overlay').fadeOut();
    }

    $('#modalStatus').modal('show');
}

$('#btnModal').on('click', function() {
    if(!empresas.value) {
        alert('Selecione uma empresa!');
        return;
    }

    consulta_status();
});

$('#modalStatus').on('hidden.bs.modal', function() {
    $('#btnModal').prop('disabled', false);
    $('#textoModal').attr('class', '');
    $('#textoModal').html('');
});

$('#btnBoleto').on('click', function() {
    
})