import { cva, type VariantProps } from 'class-variance-authority'
import { computed, defineComponent, h } from 'vue'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-mono text-caption uppercase ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        default: "rounded-lg bg-ink text-paper hover:opacity-85",
        destructive: "rounded-lg bg-rose-600 text-paper hover:opacity-85",
        outline: "rounded-lg border border-ink/20 bg-transparent text-ink hover:border-ink/50",
        secondary: "rounded-lg bg-paper-dim text-ink hover:bg-paper-line/60",
        ghost: "rounded-lg text-ink-soft hover:bg-ink/5 hover:text-ink",
        link: "text-ink underline-offset-4 hover:underline normal-case",
        full: "w-full rounded-lg bg-ink text-paper hover:opacity-85",
        "full-outline": "w-full rounded-lg border border-ink/20 bg-transparent text-ink hover:border-ink/50",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3 text-micro",
        lg: "h-11 px-6",
        xl: "h-12 px-8",
        "2xl": "h-14 px-10",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps extends VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = defineComponent({
  name: 'Button',
  props: {
    variant: {
      type: String as () => 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' | 'full' | 'full-outline',
      default: 'default'
    },
    size: {
      type: String as () => 'default' | 'sm' | 'lg' | 'icon' | 'xl' | '2xl',
      default: 'default'
    },
    asChild: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      const mergedClass = cn(buttonVariants({ variant: props.variant, size: props.size }), extraClass as string)
      return h('button', {
        class: mergedClass,
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export { buttonVariants }
