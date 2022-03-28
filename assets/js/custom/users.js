$(document).ready(e => {

  // SHOW MODAL CREATE
  $('#create').click(e => {
    $('#id-title-modal').text('Novo usuário')
    $('#id').val('')
    $('#name').val('')
    $('#email').val('')
    $('#pass').val('')
    $('#perfil').prop('checked', false)

    $('#modal').modal('show')
  })

  // SHOW MODAL EDIT
  $table = $('#datatable')
  $table.on('click', '[btn-edit]', $.proxy(onBtnEditClick))

  function onBtnEditClick(e) {
    $('#id-title-modal').text('Editar pull request')
    $('#id').val($(e.currentTarget).attr('data-id'))

    let name = $(e.currentTarget).attr('data-name')
    let email = $(e.currentTarget).attr('data-email')
    let perfil = $(e.currentTarget).attr('data-perfil')

    $('#name').val(name)
    $('#email').val(email)
    perfil == 1 ? $('#perfil').prop('checked', true) : $('#perfil').prop('checked', false)

    $('#modal').modal('show')
  }

  // REACTIVE USER
  $table.on('click', '[btn-reactivate]', $.proxy(onBtnReactivateClick))

  function onBtnReactivateClick(e) {
    let btnReactivate = $(e.currentTarget)

    swal({
        title: 'Tem certeza?',
        text: 'Uma vez reativado, poderá acessar o sistema!',
        icon: 'warning',
        buttons: true,
        dangerMode: true,
      })
      .then((willDelete) => {
        if (willDelete) {
          $.ajax({
            type: 'POST',
            url: `/reactivate-user/${btnReactivate.attr('data-id')}`,
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

  // DELETE USER
  $table.on('click', '[btn-delete]', $.proxy(onBtnDeleteClick))

  function onBtnDeleteClick(e) {
    let btnDelete = $(e.currentTarget)

    swal({
        title: 'Tem certeza?',
        text: 'Uma vez deletado, o usuário não poderá acessar o sistema!',
        icon: 'warning',
        buttons: true,
        dangerMode: true,
      })
      .then((willDelete) => {
        if (willDelete) {
          $.ajax({
            type: 'DELETE',
            url: `/delete-user/${btnDelete.attr('data-id')}`,
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
    const name              = $('#name')
    const email             = $('#email')
    const perfil            = $('input:checkbox[name=perfil]:checked')
    const pass              = $('#pass')

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
      name.val('')
      email.val('')
      pass.val('')
      $('#perfil').prop('checked', false)
    }

    if (name.val() === '' || email.val() === '') {
      alertMessage.classList.add('alert-danger')
      alertMessage.innerText = 'Preencha todos os dados corretamente.'
      alertMessage.classList.remove('hide')
      alertMessage.classList.add('show')

      clearAlert(alertMessage)

    } else if(id.val() === '') {
      $.ajax({
        type: 'POST',
        url: '/create-user',
        data: {
          name: name.val(),
          email: email.val(),
          pass: pass.val(),
          profile: perfil.val() == 'on' ? 1 : 0
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

            // clearInputs()
            clearAlert(alertMessage)

            // setTimeout(() => {
            //   location.reload()
            //   $('#modal').modal('hide')
            // }, 3000)
          }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          console.log(textStatus)
        }
      })

    } else {
      $.ajax({
        type: 'post',
        url: '/update-user',
        data: {
          id: id.val(),
          name: name.val(),
          email: email.val(),
          pass: pass.val(),
          profile: perfil.val() == 'on' ? 1 : 0
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

            // clearInputs()
            clearAlert(alertMessage)

            // setTimeout(() => {
            //   location.reload()
            //   $('#modal').modal('hide')
            // }, 3000)
          }
        },
        error: function (xmlhttprequest, textstatus, errorthrown) {
          console.log(textstatus)
        }
      })
    }
  })
})
