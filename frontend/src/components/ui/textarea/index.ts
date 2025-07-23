import { defineComponent, h } from 'vue'

export const Textarea = defineComponent({
  name: 'Textarea',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { slots, attrs, emit }) {
    return () => h('textarea', {
      class: 'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      value: props.modelValue,
      onInput: (e: Event) => {
        const target = e.target as HTMLTextAreaElement
        emit('update:modelValue', target.value)
      },
      ...attrs
    }, slots.default?.())
  }
}) 