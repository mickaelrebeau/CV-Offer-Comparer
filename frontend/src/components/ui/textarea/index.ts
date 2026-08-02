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
            "flex min-h-[200px] w-full rounded-lg border border-ink/20 bg-paper px-3 py-2.5 font-sans text-sm text-ink placeholder:text-ink-soft/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/20 disabled:cursor-not-allowed disabled:opacity-50",
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
