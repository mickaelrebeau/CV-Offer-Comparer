import { defineComponent, h } from 'vue'
import { cn } from '@/lib/utils'

export const Card = defineComponent({
  name: 'Card',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('div', {
        class: cn('rounded-2xl border bg-card text-card-foreground shadow-sm', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export const CardHeader = defineComponent({
  name: 'CardHeader',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('div', {
        class: cn('flex flex-col space-y-1.5 p-6', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export const CardTitle = defineComponent({
  name: 'CardTitle',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('h3', {
        class: cn('text-2xl font-semibold leading-none tracking-tight', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export const CardDescription = defineComponent({
  name: 'CardDescription',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('p', {
        class: cn('text-sm text-muted-foreground', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export const CardContent = defineComponent({
  name: 'CardContent',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('div', {
        class: cn('p-6 pt-0', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})

export const CardFooter = defineComponent({
  name: 'CardFooter',
  setup(props, { slots, attrs }) {
    return () => {
      const { class: extraClass, ...restAttrs } = attrs
      return h('div', {
        class: cn('flex items-center p-6 pt-0', extraClass as string),
        ...restAttrs
      }, slots.default?.())
    }
  }
})
