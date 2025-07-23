import { defineComponent, h } from 'vue'

export const Card = defineComponent({
  name: 'Card',
  setup(props, { slots, attrs }) {
    return () => h('div', {
      class: 'rounded-lg border bg-card text-card-foreground shadow-sm',
      ...attrs
    }, slots.default?.())
  }
})

export const CardHeader = defineComponent({
  name: 'CardHeader',
  setup(props, { slots, attrs }) {
    return () => h('div', {
      class: 'flex flex-col space-y-1.5 p-6',
      ...attrs
    }, slots.default?.())
  }
})

export const CardTitle = defineComponent({
  name: 'CardTitle',
  setup(props, { slots, attrs }) {
    return () => h('h3', {
      class: 'text-2xl font-semibold leading-none tracking-tight',
      ...attrs
    }, slots.default?.())
  }
})

export const CardDescription = defineComponent({
  name: 'CardDescription',
  setup(props, { slots, attrs }) {
    return () => h('p', {
      class: 'text-sm text-muted-foreground',
      ...attrs
    }, slots.default?.())
  }
})

export const CardContent = defineComponent({
  name: 'CardContent',
  setup(props, { slots, attrs }) {
    return () => h('div', {
      class: 'p-6 pt-0',
      ...attrs
    }, slots.default?.())
  }
})

export const CardFooter = defineComponent({
  name: 'CardFooter',
  setup(props, { slots, attrs }) {
    return () => h('div', {
      class: 'flex items-center p-6 pt-0',
      ...attrs
    }, slots.default?.())
  }
}) 