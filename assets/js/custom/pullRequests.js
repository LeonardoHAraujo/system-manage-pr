$(document).ready(e => {

  // SHOW MODAL CREATE
  $('#create').click(e => {
    $('#id-title-modal').text('Novo pull request')
    $('#id').val('')
    $('#autor').val('')
    $('#revisor').val('')
    $('#link').val('')
    $('#flexRadioDefault1').attr('checked', 'checked')

    $('#modal').modal('show')
  })

  // SHOW MODAL EDIT
  $table = $('#datatable')
  $table.on('click', '[btn-edit]', $.proxy(onBtnEditClick))

  function onBtnEditClick(e) {
    $('#id-title-modal').text('Editar pull request')
    $('#id').val($(e.currentTarget).attr('data-id'))

    const r1 = $('#flexRadioDefault1')
    const r2 = $('#flexRadioDefault2')
    const r3 = $('#flexRadioDefault3')

    let autor = $(e.currentTarget).attr('data-autor')
    let revisor = $(e.currentTarget).attr('data-revisor')
    let link = $(e.currentTarget).attr('data-link')
    let situacao = $(e.currentTarget).attr('data-situacao')

    $('#autor').val(autor)
    $('#revisor').val(revisor)
    $('#link').val(link)

    if (situacao == 0) {
      r3.prop('checked', false)
      r2.prop('checked', false)
      r1.prop('checked', true)

    } else if (situacao == 1) {
      r3.prop('checked', false)
      r1.prop('checked', false)
      r2.prop('checked', true)

    } else {
      r1.prop('checked', false)
      r2.prop('checked', false)
      r3.prop('checked', true)
    }

    $('#modal').modal('show')
  }

  // DELETE USER
  $table.on('click', '[btn-delete]', $.proxy(onBtnDeleteClick))

  function onBtnDeleteClick(e) {
    let btnDelete = $(e.currentTarget)

    swal({
        title: 'Tem certeza?',
        text: 'Uma vez deletado, o PR não poderá ser recuperado!',
        icon: 'warning',
        buttons: true,
        dangerMode: true,
      })
      .then((willDelete) => {
        if (willDelete) {
          $.ajax({
            type: 'DELETE',
            url: `/delete-pr/${btnDelete.attr('data-id')}`,
            data: {},
            success: function (data) {
                location.reload()
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus)
            }
          })
        } else {
          swal('Você escolheu cancelar a exclusão!');
        }
      });
  }

  // SUBMIT MODAL
  $('#confirm').click(e => {
    e.preventDefault();

    const id                = $('#id')
    const autor             = $('#autor')
    const revisor           = $('#revisor')
    const link              = $('#link ')
    const situacao          = $(`input[name=flexRadioDefault]:checked`)

    let alertMessage = document.querySelector('#alert-message')

    function clearAlert(field) {
      if(field.text !== '') {
        setTimeout(() => {
          field.classList.remove('show')
          field.classList.add('hide')
          field.classList.remove('alert-danger')
          field.innerText = ''
        }, 4000)
      }
    }

    function clearInputs() {
      autor.val('')
      revisor.val('')
      link.val('')
    }

    if (autor.val() === '' || revisor.val() === '' || link.val() === '') {
      alertMessage.classList.add('alert-danger')
      alertMessage.innerText = 'Preencha todos os dados corretamente.'
      alertMessage.classList.remove('hide')
      alertMessage.classList.add('show')

      clearAlert(alertMessage)

    } else if(id.val() === '') {
      $.ajax({
        type: 'POST',
        url: '/create-pr',
        data: {
          autor: autor.val(),
          revisor: revisor.val(),
          link: link.val(),
          situacao: situacao.val()
        },
        success: function (data) {
          if(data.status === 200) {
            alertMessage.classList.add('alert-success')
            alertMessage.innerText = data.message
            alertMessage.classList.remove('hide')
            alertMessage.classList.add('show')

            clearAlert(alertMessage)

            setTimeout(() => {
              location.reload()
              $('#modal').modal('hide')
            }, 3000)

          } else if(data.status === 400) {
            alertMessage.classList.add('alert-success')
            alertMessage.innerText = data.message
            alertMessage.classList.remove('hide')
            alertMessage.classList.add('show')

            clearInputs()
            clearAlert(alertMessage)

            setTimeout(() => {
              location.reload()
              $('#modal').modal('hide')
            }, 3000)
          }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          console.log(textStatus)
        }
      })

    } else {
      $.ajax({
        type: 'post',
        url: '/update-pr',
        data: {
          id: id.val(),
          autor: autor.val(),
          revisor: revisor.val(),
          link: link.val(),
          situacao: situacao.val()
        },
        success: function (data) {
          if(data.status === 200) {
            alertMessage.classList.add('alert-success')
            alertMessage.innerText = data.message
            alertMessage.classList.remove('hide')
            alertMessage.classList.add('show')

            clearAlert(alertMessage)

            setTimeout(() => {
              location.reload()
              $('#modal').modal('hide')
            }, 3000)

          } else if(data.status === 400) {
            alertMessage.classList.add('alert-danger')
            alertMessage.innerText = data.message
            alertMessage.classList.remove('hide')
            alertMessage.classList.add('show')

            clearinputs()
            clearAlert(alertMessage)

            setTimeout(() => {
              location.reload()
              $('#modal').modal('hide')
            }, 3000)
          }
        },
        error: function (xmlhttprequest, textstatus, errorthrown) {
          console.log(textstatus)
        }
      })
    }
  })
})
