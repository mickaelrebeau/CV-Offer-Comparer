import { cva, type VariantProps } from 'class-variance-authority'
import { computed, defineComponent, h } from 'vue'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline:
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary:
          'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps extends VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = defineComponent({
  name: 'Button',
  props: {
    variant: {
      type: String as () => 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link',
      default: 'default'
    },
    size: {
      type: String as () => 'default' | 'sm' | 'lg' | 'icon',
      default: 'default'
    },
    asChild: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { slots, attrs }) {
    const computedClass = computed(() => {
      return buttonVariants({ variant: props.variant, size: props.size })
    })

    return () => h('button', {
      class: computedClass.value,
      ...attrs
    }, slots.default?.())
  }
})

export { buttonVariants } 