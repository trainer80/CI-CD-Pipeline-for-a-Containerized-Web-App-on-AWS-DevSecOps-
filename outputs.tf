output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "app_url" {
  description = "URL of the deployed app"
  value       = "http://${aws_instance.app.public_ip}"
}
