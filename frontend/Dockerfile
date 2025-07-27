# ─── Etapa de build ────────────────────────────────────────────────────────────
FROM node:18-alpine AS build
WORKDIR /app

# Copiamos los archivos de dependencias
COPY package.json package-lock.json ./

# Instalamos todo (incluye devDependencies como vite y react-router-dom)
RUN npm install

# Copiamos el resto del código fuente
COPY . .

# Construimos la aplicación
RUN npm run build

# ─── Etapa de producción ──────────────────────────────────────────────────────
FROM nginx:alpine

# Copiamos el resultado del build a la carpeta que sirve Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Exponemos el puerto 80
EXPOSE 80

# Arrancamos Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]
