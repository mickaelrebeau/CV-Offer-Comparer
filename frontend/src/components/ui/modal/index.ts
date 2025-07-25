import { defineComponent, h, ref, watch } from 'vue'

export interface ModalProps {
  isOpen: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'error' | 'success'
  showCancel?: boolean
}

export const Modal = defineComponent({
  name: 'Modal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: 'Confirmer'
    },
    cancelText: {
      type: String,
      default: 'Annuler'
    },
    type: {
      type: String as () => 'info' | 'warning' | 'error' | 'success',
      default: 'info'
    },
    showCancel: {
      type: Boolean,
      default: true
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  setup(props, { slots, emit }) {
    const isVisible = ref(props.isOpen)

    watch(() => props.isOpen, (newValue) => {
      isVisible.value = newValue
    })

    const handleConfirm = () => {
      emit('confirm')
    }

    const handleCancel = () => {
      emit('cancel')
    }

    const handleClose = () => {
      emit('close')
    }

    const getTypeClasses = () => {
      switch (props.type) {
        case 'warning':
          return 'border-yellow-500 bg-yellow-50 text-yellow-800'
        case 'error':
          return 'border-red-500 bg-red-50 text-red-800'
        case 'success':
          return 'border-green-500 bg-green-50 text-green-800'
        default:
          return 'border-blue-500 bg-blue-50 text-blue-800'
      }
    }

    const getIconClasses = () => {
      switch (props.type) {
        case 'warning':
          return 'text-yellow-500'
        case 'error':
          return 'text-red-500'
        case 'success':
          return 'text-green-500'
        default:
          return 'text-blue-500'
      }
    }

    return () => {
      if (!isVisible.value) return null

      return h('div', {
        class: 'fixed inset-0 z-50 flex items-center justify-center'
      }, [
        // Overlay
        h('div', {
          class: 'absolute inset-0 bg-black bg-opacity-50',
          onClick: handleClose
        }),
        // Modal
        h('div', {
          class: 'relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6'
        }, [
          // Header
          h('div', {
            class: 'flex items-center justify-between mb-4'
          }, [
            h('h3', {
              class: 'text-lg font-semibold text-gray-900'
            }, props.title),
            h('button', {
              class: 'text-gray-400 hover:text-gray-600',
              onClick: handleClose
            }, '×')
          ]),
          // Content
          h('div', {
            class: 'mb-6'
          }, [
            h('div', {
              class: `p-4 rounded-md border ${getTypeClasses()}`
            }, [
              h('div', {
                class: 'flex items-start'
              }, [
                h('div', {
                  class: `flex-shrink-0 ${getIconClasses()}`
                }, [
                  props.type === 'warning' && h('svg', {
                    class: 'h-5 w-5',
                    fill: 'currentColor',
                    viewBox: '0 0 20 20'
                  }, [
                    h('path', {
                      'fill-rule': 'evenodd',
                      d: 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
                      'clip-rule': 'evenodd'
                    })
                  ]),
                  props.type === 'error' && h('svg', {
                    class: 'h-5 w-5',
                    fill: 'currentColor',
                    viewBox: '0 0 20 20'
                  }, [
                    h('path', {
                      'fill-rule': 'evenodd',
                      d: 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
                      'clip-rule': 'evenodd'
                    })
                  ]),
                  props.type === 'success' && h('svg', {
                    class: 'h-5 w-5',
                    fill: 'currentColor',
                    viewBox: '0 0 20 20'
                  }, [
                    h('path', {
                      'fill-rule': 'evenodd',
                      d: 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
                      'clip-rule': 'evenodd'
                    })
                  ]),
                  props.type === 'info' && h('svg', {
                    class: 'h-5 w-5',
                    fill: 'currentColor',
                    viewBox: '0 0 20 20'
                  }, [
                    h('path', {
                      'fill-rule': 'evenodd',
                      d: 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z',
                      'clip-rule': 'evenodd'
                    })
                  ])
                ]),
                h('div', {
                  class: 'ml-3'
                }, [
                  h('p', {
                    class: 'text-sm'
                  }, props.message)
                ])
              ])
            ])
          ]),
          // Footer
          h('div', {
            class: 'flex justify-end space-x-3'
          }, [
            props.showCancel && h('button', {
              class: 'px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
              onClick: handleCancel
            }, props.cancelText),
            h('button', {
              class: `px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                props.type === 'error' 
                  ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
                  : props.type === 'warning'
                  ? 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
                  : props.type === 'success'
                  ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
                  : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
              }`,
              onClick: handleConfirm
            }, props.confirmText)
          ])
        ])
      ])
    }
  }
}) 