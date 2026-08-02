import { defineComponent, h } from 'vue'
import { cn } from '@/lib/utils'

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
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h(
        "textarea",
        {
          class: cn(
            "flex min-h-[200px] w-full h-full rounded-md border border-input px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 bg-background text-foreground border-border",
            extraClass as string
          ),
          value: props.modelValue,
          onInput: (e: Event) => {
            const target = e.target as HTMLTextAreaElement;
            emit("update:modelValue", target.value);
          },
          ...restAttrs,
        },
        slots.default?.()
      );
    }
  }
})
