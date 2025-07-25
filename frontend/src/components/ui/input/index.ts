import { defineComponent, h, ref, computed } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'

export const Input = defineComponent({
  name: 'Input',
  props: {
    type: {
      type: String,
      default: 'text'
    },
    modelValue: {
      type: [String, Number],
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    required: {
      type: Boolean,
      default: false
    },
    minlength: {
      type: [String, Number],
      default: undefined
    },
    id: {
      type: String,
      default: ''
    },
    showPasswordToggle: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit, attrs }) {
    const showPassword = ref(false)
    
    const inputType = computed(() => {
      if (props.type === 'password' && props.showPasswordToggle) {
        return showPassword.value ? 'text' : 'password'
      }
      return props.type
    })

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }

    const handleInput = (event: Event) => {
      const target = event.target as HTMLInputElement
      emit('update:modelValue', target.value)
    }

    return () => {
      const inputElement = h('input', {
        type: inputType.value,
        value: props.modelValue,
        placeholder: props.placeholder,
        required: props.required,
        minlength: props.minlength,
        id: props.id,
        class: 'w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        onInput: handleInput,
        ...attrs
      })

      if (props.type === 'password' && props.showPasswordToggle) {
        return h('div', {
          class: 'relative'
        }, [
          inputElement,
          h('button', {
            type: 'button',
            class: 'absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground',
            onClick: togglePasswordVisibility
          }, [
            h(showPassword.value ? EyeOff : Eye, {
              class: 'h-4 w-4'
            })
          ])
        ])
      }

      return inputElement
    }
  }
}) 