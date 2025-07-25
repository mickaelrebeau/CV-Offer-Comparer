import { defineComponent, h, ref, watch } from 'vue'

export interface NotificationProps {
  isOpen: boolean
  message: string
  type?: 'info' | 'warning' | 'error' | 'success'
  duration?: number
}

export const Notification = defineComponent({
  name: 'Notification',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    type: {
      type: String as () => 'info' | 'warning' | 'error' | 'success',
      default: 'info'
    },
    duration: {
      type: Number,
      default: 5000
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const isVisible = ref(props.isOpen)
    let timeoutId: number | null = null

    watch(() => props.isOpen, (newValue) => {
      isVisible.value = newValue
      if (newValue && props.duration > 0) {
        if (timeoutId) clearTimeout(timeoutId)
        timeoutId = setTimeout(() => {
          emit('close')
        }, props.duration)
      }
    })

    const handleClose = () => {
      if (timeoutId) clearTimeout(timeoutId)
      emit('close')
    }

    const getTypeClasses = () => {
      switch (props.type) {
        case 'warning':
          return 'bg-yellow-50 border-yellow-400 text-yellow-800'
        case 'error':
          return 'bg-red-50 border-red-400 text-red-800'
        case 'success':
          return 'bg-green-50 border-green-400 text-green-800'
        default:
          return 'bg-blue-50 border-blue-400 text-blue-800'
      }
    }

    const getIconClasses = () => {
      switch (props.type) {
        case 'warning':
          return 'text-yellow-400'
        case 'error':
          return 'text-red-400'
        case 'success':
          return 'text-green-400'
        default:
          return 'text-blue-400'
      }
    }

    return () => {
      if (!isVisible.value) return null

      return h('div', {
        class: 'fixed top-4 right-4 z-50 max-w-sm w-full'
      }, [
        h('div', {
          class: `p-4 rounded-md border ${getTypeClasses()} shadow-lg`
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
              class: 'ml-3 flex-1'
            }, [
              h('p', {
                class: 'text-sm font-medium'
              }, props.message)
            ]),
            h('div', {
              class: 'ml-4 flex-shrink-0'
            }, [
              h('button', {
                class: 'inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600',
                onClick: handleClose
              }, [
                h('span', { class: 'sr-only' }, 'Fermer'),
                h('svg', {
                  class: 'h-5 w-5',
                  fill: 'currentColor',
                  viewBox: '0 0 20 20'
                }, [
                  h('path', {
                    'fill-rule': 'evenodd',
                    d: 'M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z',
                    'clip-rule': 'evenodd'
                  })
                ])
              ])
            ])
          ])
        ])
      ])
    }
  }
}) 